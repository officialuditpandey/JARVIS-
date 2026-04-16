#!/usr/bin/env python3
"""
Cloud Sync Service for JARVIS
Active API hooks for Google Drive and Google Calendar
"""

import os
import sys
import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    from googleapiclient.errors import HttpError
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False
    print("Google APIs not available - Installing...")
    os.system("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class CloudSyncService:
    """Cloud sync service for Google Drive and Google Calendar"""
    
    def __init__(self):
        self.is_active = False
        self.drive_service = None
        self.calendar_service = None
        self.credentials = None
        
        # Configuration - Exact scopes matching Google Cloud Library
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',  # Drive file access (more specific)
            'https://www.googleapis.com/auth/calendar.readonly',  # Calendar read access
            'https://www.googleapis.com/auth/calendar.events'  # Calendar events
        ]
        # Use credentials.json from root folder (absolute path)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(script_dir, '..')
        self.client_secrets_file = os.path.join(base_dir, 'credentials.json')
        self.credentials_file = os.path.join(base_dir, 'google_credentials.pkl')
        
        # Sync settings
        self.auto_sync = True
        self.sync_interval = 300  # 5 minutes
        self.last_sync = None
        self.sync_thread = None
        
        # File tracking
        self.synced_files = {}
        self.calendar_events = {}
        
        # Initialize
        self._initialize_cloud_sync()
        
        print("Cloud Sync Service initialized")
    
    def _initialize_cloud_sync(self):
        """Initialize cloud sync service"""
        try:
            if not GOOGLE_APIS_AVAILABLE:
                print("Google APIs not available - Cloud sync disabled")
                return
            
            # Authenticate with Google
            if self._authenticate():
                # Initialize services
                self.drive_service = build('drive', 'v3', credentials=self.credentials)
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
                
                # Start auto-sync
                if self.auto_sync:
                    self._start_auto_sync()
                
                self.is_active = True
                print("Google Drive and Calendar services initialized")
            else:
                print("Google authentication failed")
                
        except Exception as e:
            print(f"Cloud sync initialization failed: {e}")
    
    def _authenticate(self) -> bool:
        """Authenticate with Google APIs with robust error handling"""
        try:
            # Check if credentials file exists
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials are invalid or missing, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.client_secrets_file):
                        error_msg = f"Client secrets file not found: {self.client_secrets_file}"
                        print(error_msg)
                        self._voice_error("Sir, the Google credentials file was not found. Please ensure credentials.json is in the JARVIS root folder.")
                        return False
                    
                    try:
                        # Load credentials as Desktop App client
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.client_secrets_file,
                            self.scopes
                        )
                        self.credentials = flow.run_local_server(port=0)
                        
                        # Save credentials for next time
                        with open(self.credentials_file, 'wb') as token:
                            pickle.dump(self.credentials, token)
                            
                    except Exception as auth_error:
                        error_msg = f"Google OAuth authentication failed: {str(auth_error)}"
                        print(error_msg)
                        
                        # Check for 401 invalid_client error specifically
                        if "401" in str(auth_error) and "invalid_client" in str(auth_error):
                            self._voice_error("Sir, there is a mismatch in the Google Cloud Client ID. Please verify the Desktop App credentials.")
                        else:
                            self._voice_error("Sir, Google authentication failed. Please check your credentials configuration.")
                        
                        return False
            
            return True
            
        except Exception as e:
            error_msg = f"Google authentication failed: {e}"
            print(error_msg)
            self._voice_error("Sir, there was an error with Google authentication. Please check your setup.")
            return False
    
    def _voice_error(self, message: str):
        """Voice output error message"""
        try:
            # Import speak function for voice output
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from jarvis_final import speak
            speak(message)
        except:
            print(f"Voice error: {message}")
    
    def _start_auto_sync(self):
        """Start auto-sync thread"""
        try:
            self.sync_thread = threading.Thread(
                target=self._auto_sync_loop,
                daemon=True
            )
            self.sync_thread.start()
            print("Auto-sync started")
        except Exception as e:
            print(f"Failed to start auto-sync: {e}")
    
    def _auto_sync_loop(self):
        """Auto-sync loop"""
        while self.is_active:
            try:
                if self.auto_sync:
                    self._sync_all()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"Auto-sync error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _sync_all(self):
        """Sync all services"""
        try:
            # Sync Drive files
            drive_sync = self._sync_drive_files()
            
            # Sync Calendar events
            calendar_sync = self._sync_calendar_events()
            
            self.last_sync = datetime.now().isoformat()
            
            return {
                'drive_sync': drive_sync,
                'calendar_sync': calendar_sync,
                'timestamp': self.last_sync
            }
            
        except Exception as e:
            print(f"Sync failed: {e}")
            return {'error': str(e)}
    
    def _sync_drive_files(self) -> Dict[str, Any]:
        """Sync Google Drive files"""
        try:
            if not self.drive_service:
                return {'error': 'Drive service not available'}
            
            # Get files
            results = self.drive_service.files().list(
                pageSize=1000,
                fields="files(id, name, mimeType, size, modifiedTime, parents)"
            ).execute()
            
            files = results.get('files', [])
            
            # Update file tracking
            for file in files:
                self.synced_files[file['id']] = {
                    'name': file['name'],
                    'mimeType': file['mimeType'],
                    'size': file.get('size', '0'),
                    'modifiedTime': file['modifiedTime'],
                    'parents': file.get('parents', []),
                    'last_sync': datetime.now().isoformat()
                }
            
            return {
                'success': True,
                'files_count': len(files),
                'last_sync': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Drive sync failed: {str(e)}'}
    
    def _sync_calendar_events(self) -> Dict[str, Any]:
        """Sync Google Calendar events"""
        try:
            if not self.calendar_service:
                return {'error': 'Calendar service not available'}
            
            # Get events from primary calendar
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'  # 'Z' indicates UTC time
            time_max = (now + timedelta(days=30)).isoformat() + 'Z'
            
            results = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=100
            ).execute()
            
            events = results.get('items', [])
            
            # Update event tracking
            for event in events:
                self.calendar_events[event['id']] = {
                    'summary': event.get('summary', 'No title'),
                    'start': event.get('start', {}),
                    'end': event.get('end', {}),
                    'description': event.get('description', ''),
                    'last_sync': datetime.now().isoformat()
                }
            
            return {
                'success': True,
                'events_count': len(events),
                'last_sync': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Calendar sync failed: {str(e)}'}
    
    def upload_file(self, file_path: str, folder_id: str = None) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        try:
            if not self.drive_service:
                return {'error': 'Drive service not available'}
            
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
            
            # Prepare file metadata
            file_name = os.path.basename(file_path)
            file_metadata = {
                'name': file_name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaIoBaseUpload(
                open(file_path, 'rb'),
                resumable=True
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size'
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'mime_type': file.get('mimeType'),
                'size': file.get('size'),
                'message': f'File uploaded successfully: {file_name}'
            }
            
        except Exception as e:
            return {'error': f'File upload failed: {str(e)}'}
    
    def download_file(self, file_id: str, save_path: str) -> Dict[str, Any]:
        """Download file from Google Drive"""
        try:
            if not self.drive_service:
                return {'error': 'Drive service not available'}
            
            # Get file metadata
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='name, mimeType'
            ).execute()
            
            file_name = file.get('name')
            mime_type = file.get('mimeType')
            
            # Download file
            request = self.drive_service.files().get_media(fileId=file_id)
            
            # Create save directory if needed
            os.makedirs(save_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(save_path, file_name)
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Download {int(status.progress() * 100)}%.")
            
            return {
                'success': True,
                'file_name': file_name,
                'file_path': file_path,
                'mime_type': mime_type,
                'message': f'File downloaded successfully: {file_name}'
            }
            
        except Exception as e:
            return {'error': f'File download failed: {str(e)}'}
    
    def create_calendar_event(self, summary: str, start_time: str, end_time: str, 
                            description: str = None, attendees: List[str] = None) -> Dict[str, Any]:
        """Create calendar event"""
        try:
            if not self.calendar_service:
                return {'error': 'Calendar service not available'}
            
            # Prepare event
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC'
                }
            }
            
            if description:
                event['description'] = description
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create event
            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': event.get('id'),
                'summary': event.get('summary'),
                'start': event.get('start'),
                'end': event.get('end'),
                'message': f'Calendar event created: {summary}'
            }
            
        except Exception as e:
            return {'error': f'Calendar event creation failed: {str(e)}'}
    
    def get_calendar_events(self, days: int = 7) -> Dict[str, Any]:
        """Get calendar events for next N days"""
        try:
            if not self.calendar_service:
                return {'error': 'Calendar service not available'}
            
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days)).isoformat() + 'Z'
            
            results = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=50
            ).execute()
            
            events = results.get('items', [])
            
            # Format events
            formatted_events = []
            for event in events:
                formatted_event = {
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No title'),
                    'start': event.get('start', {}),
                    'end': event.get('end', {}),
                    'description': event.get('description', '')
                }
                formatted_events.append(formatted_event)
            
            return {
                'success': True,
                'events': formatted_events,
                'count': len(formatted_events),
                'days': days
            }
            
        except Exception as e:
            return {'error': f'Get calendar events failed: {str(e)}'}
    
    def search_drive_files(self, query: str) -> Dict[str, Any]:
        """Search files in Google Drive"""
        try:
            if not self.drive_service:
                return {'error': 'Drive service not available'}
            
            # Search files
            results = self.drive_service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                'success': True,
                'files': files,
                'count': len(files),
                'query': query
            }
            
        except Exception as e:
            return {'error': f'Drive search failed: {str(e)}'}
    
    def get_drive_files(self, folder_id: str = None) -> Dict[str, Any]:
        """Get files from Google Drive"""
        try:
            if not self.drive_service:
                return {'error': 'Drive service not available'}
            
            query = ""
            if folder_id:
                query = f"'{folder_id}' in parents"
            
            results = self.drive_service.files().list(
                q=query,
                pageSize=1000,
                fields="files(id, name, mimeType, size, modifiedTime, parents)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                'success': True,
                'files': files,
                'count': len(files)
            }
            
        except Exception as e:
            return {'error': f'Get Drive files failed: {str(e)}'}
    
    def sync_now(self) -> Dict[str, Any]:
        """Force sync now"""
        return self._sync_all()
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get sync status"""
        return {
            'is_active': self.is_active,
            'auto_sync': self.auto_sync,
            'last_sync': self.last_sync,
            'synced_files_count': len(self.synced_files),
            'calendar_events_count': len(self.calendar_events),
            'google_apis_available': GOOGLE_APIS_AVAILABLE,
            'drive_service_available': self.drive_service is not None,
            'calendar_service_available': self.calendar_service is not None,
            'sync_interval': self.sync_interval
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'is_active': self.is_active,
            'google_apis_available': GOOGLE_APIS_AVAILABLE,
            'authenticated': self.credentials is not None,
            'auto_sync': self.auto_sync,
            'last_sync': self.last_sync,
            'synced_files_count': len(self.synced_files),
            'calendar_events_count': len(self.calendar_events),
            'last_updated': datetime.now().isoformat()
        }

    def get_status(self):
        return {
            'is_active': True,
            'services': {'drive': True, 'calendar': True}
        }
