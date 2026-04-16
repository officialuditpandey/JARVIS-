#!/usr/bin/env python3
"""
Cloud Workspace Service for JARVIS
Full native access to Google Drive and Calendar
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pickle
import webbrowser

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    print("Google API not available - Installing...")
    os.system("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        GOOGLE_API_AVAILABLE = True
    except ImportError:
        GOOGLE_API_AVAILABLE = False

class CloudWorkspaceService:
    """Cloud Workspace service for Google Drive and Calendar access"""
    
    def __init__(self):
        self.is_active = False
        self.is_authenticated = False
        self.credentials = None
        self.drive_service = None
        self.calendar_service = None
        
        # Authentication
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
        # Token storage
        self.token_file = 'cloud_workspace_token.json'
        self.credentials_file = 'cloud_workspace_credentials.json'
        
        # Cache
        self.drive_cache = {}
        self.calendar_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
        # Performance metrics
        self.api_calls = 0
        self.files_uploaded = 0
        self.files_downloaded = 0
        self.events_created = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_cloud_workspace()
        
        print("Cloud Workspace Service initialized")
    
    def _initialize_cloud_workspace(self):
        """Initialize cloud workspace services"""
        try:
            if not GOOGLE_API_AVAILABLE:
                print("Google APIs not available")
                return
            
            # Check for existing credentials
            if os.path.exists(self.token_file):
                self.credentials = pickle.load(open(self.token_file, 'rb'))
                
                # Refresh if expired
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials()
            
            # Build services if authenticated
            if self.credentials and self.credentials.valid:
                self._build_services()
                self.is_authenticated = True
                print("Cloud workspace authenticated")
            
        except Exception as e:
            print(f"Cloud workspace initialization failed: {e}")
    
    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Google Workspace"""
        try:
            if not GOOGLE_API_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Google APIs not available'
                }
            
            # Create credentials file if it doesn't exist
            if not os.path.exists(self.credentials_file):
                self._create_credentials_file()
            
            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes)
            
            self.credentials = flow.run_local_server(port=0)
            
            # Save credentials
            self._save_credentials()
            
            # Build services
            self._build_services()
            
            self.is_authenticated = True
            self.is_active = True
            
            return {
                'success': True,
                'message': 'Successfully authenticated with Google Workspace'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Authentication failed: {str(e)}'
            }
    
    def _create_credentials_file(self):
        """Create a placeholder credentials file with instructions"""
        try:
            instructions = """
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID_HERE",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET_HERE",
    "redirect_uris": ["http://localhost"]
  }
}

Instructions:
1. Go to Google Cloud Console (console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google Drive API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Copy client_id and client_secret to this file
6. Run authentication again
"""
            
            with open(self.credentials_file, 'w') as f:
                f.write(instructions)
            
            print(f"Created credentials file: {self.credentials_file}")
            print("Please edit the file with your Google Cloud credentials")
            
        except Exception as e:
            print(f"Failed to create credentials file: {e}")
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            if self.credentials:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
        except Exception as e:
            print(f"Failed to save credentials: {e}")
    
    def _build_services(self):
        """Build Google API services"""
        try:
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
            print("Google services built successfully")
        except Exception as e:
            print(f"Failed to build services: {e}")
    
    def upload_file(self, file_path: str, folder_id: str = None, 
                   description: str = None) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File {file_path} not found'
                }
            
            # Prepare file metadata
            file_name = os.path.basename(file_path)
            mime_type = self._get_mime_type(file_path)
            
            file_metadata = {
                'name': file_name,
                'description': description or f'Uploaded by JARVIS on {datetime.now().isoformat()}'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime'
            ).execute()
            
            self.files_uploaded += 1
            self.api_calls += 1
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'size': file.get('size'),
                'mime_type': file.get('mimeType'),
                'created_time': file.get('createdTime'),
                'message': f'File {file_name} uploaded successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def download_file(self, file_id: str, save_path: str = None) -> Dict[str, Any]:
        """Download file from Google Drive"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Get file metadata
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='name,size,mimeType'
            ).execute()
            
            # Download file
            request = self.drive_service.files().get_media(fileId=file_id)
            
            if save_path is None:
                save_path = file['name']
            
            with open(save_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            self.files_downloaded += 1
            self.api_calls += 1
            
            return {
                'success': True,
                'file_name': file['name'],
                'size': file['size'],
                'mime_type': file['mimeType'],
                'save_path': save_path,
                'message': f'File {file["name"]} downloaded successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def list_files(self, query: str = None, folder_id: str = None, 
                   max_results: int = 50) -> Dict[str, Any]:
        """List files in Google Drive"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Build query
            search_query = "trashed=false"
            if query:
                search_query += f" and name contains '{query}'"
            if folder_id:
                search_query += f" and '{folder_id}' in parents"
            
            # List files
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=max_results,
                fields="files(id,name,size,mimeType,createdTime,modifiedTime,parents)"
            ).execute()
            
            files = results.get('files', [])
            
            self.api_calls += 1
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files),
                'query': search_query,
                'message': f'Found {len(files)} files'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File listing failed: {str(e)}'
            }
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict[str, Any]:
        """Create folder in Google Drive"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id,name,createdTime'
            ).execute()
            
            self.api_calls += 1
            
            return {
                'success': True,
                'folder_id': folder.get('id'),
                'folder_name': folder.get('name'),
                'created_time': folder.get('createdTime'),
                'message': f'Folder {folder_name} created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Folder creation failed: {str(e)}'
            }
    
    def search_files(self, query: str, file_type: str = None) -> Dict[str, Any]:
        """Search files in Google Drive"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Build search query
            search_query = f"name contains '{query}' and trashed=false"
            
            if file_type:
                type_mapping = {
                    'document': 'application/vnd.google-apps.document',
                    'spreadsheet': 'application/vnd.google-apps.spreadsheet',
                    'presentation': 'application/vnd.google-apps.presentation',
                    'pdf': 'application/pdf',
                    'image': 'image/',
                    'video': 'video/',
                    'audio': 'audio/'
                }
                
                if file_type in type_mapping:
                    mime_type = type_mapping[file_type]
                    if file_type in ['image', 'video', 'audio']:
                        search_query += f" and mimeType contains '{mime_type}'"
                    else:
                        search_query += f" and mimeType = '{mime_type}'"
            
            # Search files
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=50,
                fields="files(id,name,size,mimeType,createdTime,modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            self.api_calls += 1
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files),
                'query': search_query,
                'message': f'Found {len(files)} files matching "{query}"'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Search failed: {str(e)}'
            }
    
    def create_calendar_event(self, title: str, start_time: str, end_time: str,
                            description: str = None, location: str = None,
                            attendees: List[str] = None) -> Dict[str, Any]:
        """Create calendar event"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Prepare event
            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC'
                }
            }
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create event
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            self.events_created += 1
            self.api_calls += 1
            
            return {
                'success': True,
                'event_id': created_event.get('id'),
                'title': title,
                'start_time': start_time,
                'end_time': end_time,
                'event_link': created_event.get('htmlLink'),
                'message': f'Calendar event "{title}" created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Event creation failed: {str(e)}'
            }
    
    def list_calendar_events(self, start_date: str = None, end_date: str = None,
                           max_results: int = 50) -> Dict[str, Any]:
        """List calendar events"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Build time range
            time_min = None
            time_max = None
            
            if start_date:
                time_min = start_date
            if end_date:
                time_max = end_date
            else:
                # Default to next 30 days
                time_max = (datetime.now() + timedelta(days=30)).isoformat() + 'Z'
            
            # List events
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            self.api_calls += 1
            
            return {
                'success': True,
                'events': events,
                'total_events': len(events),
                'time_range': {
                    'start': time_min,
                    'end': time_max
                },
                'message': f'Found {len(events)} calendar events'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Event listing failed: {str(e)}'
            }
    
    def update_calendar_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update calendar event"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Update event
            updated_event = self.calendar_service.events().patch(
                calendarId='primary',
                eventId=event_id,
                body=updates
            ).execute()
            
            self.api_calls += 1
            
            return {
                'success': True,
                'event_id': event_id,
                'updated_fields': list(updates.keys()),
                'event_link': updated_event.get('htmlLink'),
                'message': f'Calendar event {event_id} updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Event update failed: {str(e)}'
            }
    
    def delete_calendar_event(self, event_id: str) -> Dict[str, Any]:
        """Delete calendar event"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            self.api_calls += 1
            
            return {
                'success': True,
                'event_id': event_id,
                'message': f'Calendar event {event_id} deleted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Event deletion failed: {str(e)}'
            }
    
    def get_drive_usage(self) -> Dict[str, Any]:
        """Get Google Drive storage usage"""
        try:
            if not self.is_authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
            # Get about information
            about = self.drive_service.about().get(
                fields='storageQuota,user,storageQuota'
            ).execute()
            
            self.api_calls += 1
            
            return {
                'success': True,
                'usage': about,
                'message': 'Drive usage information retrieved'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Drive usage check failed: {str(e)}'
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        try:
            return {
                'is_authenticated': self.is_authenticated,
                'is_active': self.is_active,
                'api_calls': self.api_calls,
                'files_uploaded': self.files_uploaded,
                'files_downloaded': self.files_downloaded,
                'events_created': self.events_created,
                'drive_service_active': self.drive_service is not None,
                'calendar_service_active': self.calendar_service is not None,
                'last_activity': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Status check failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get cloud workspace service status"""
        return {
            'is_active': self.is_active,
            'is_authenticated': self.is_authenticated,
            'google_api_available': GOOGLE_API_AVAILABLE,
            'credentials_file_exists': os.path.exists(self.credentials_file),
            'token_file_exists': os.path.exists(self.token_file),
            'api_calls': self.api_calls,
            'files_uploaded': self.files_uploaded,
            'files_downloaded': self.files_downloaded,
            'events_created': self.events_created,
            'last_updated': datetime.now().isoformat()
        }
