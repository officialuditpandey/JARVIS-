"""
Scholar Service for JARVIS - Study Mode and Learning Features
Features 6-10: Study Mode, Auto-Flashcard, Progress Bar, Note Taking, Research Assistant
"""

import os
import json
import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {
        'scholar_pack': {
            'study_mode': {'enabled': True, 'block_sites': ['facebook.com', 'twitter.com'], 'focus_duration': 3600},
            'auto_flashcard': {'enabled': True, 'output_dir': 'flashcards/', 'format': 'json'},
            'progress_bar': {'enabled': True, 'style': 'modern'},
            'note_taking': {'enabled': True, 'auto_save': True, 'format': 'markdown'},
            'research_assistant': {'enabled': True, 'sources': ['wikipedia']}
        }
    }

class ScholarService:
    """Scholar service for study mode and learning features"""
    
    def __init__(self):
        self.study_mode_active = False
        self.focus_start_time = None
        self.flashcards = []
        self.progress_data = {}
        self.notes = []
        self.study_thread = None
        self.stop_event = threading.Event()
        
    # FEATURE 6: STUDY MODE
    def start_study_mode(self, duration_minutes: int = 60) -> bool:
        """Start study mode with website blocking"""
        if not CONFIG['scholar_pack']['study_mode']['enabled']:
            return False
        
        try:
            self.study_mode_active = True
            self.focus_start_time = time.time()
            
            # Block distracting websites
            self.block_websites()
            
            # Start focus timer in background
            self.stop_event.clear()
            self.study_thread = threading.Thread(
                target=self._study_mode_monitor, 
                args=(duration_minutes * 60,),
                daemon=True
            )
            self.study_thread.start()
            
            self.log_study_event("STUDY_MODE_STARTED", f"Focus session started for {duration_minutes} minutes")
            return True
            
        except Exception as e:
            print(f"Failed to start study mode: {e}")
            return False
    
    def stop_study_mode(self) -> bool:
        """Stop study mode and unblock websites"""
        try:
            self.study_mode_active = False
            self.stop_event.set()
            
            if self.study_thread and self.study_thread.is_alive():
                self.study_thread.join(timeout=5)
            
            # Unblock websites
            self.unblock_websites()
            
            elapsed = time.time() - self.focus_start_time if self.focus_start_time else 0
            self.log_study_event("STUDY_MODE_STOPPED", f"Focus session ended. Duration: {elapsed/60:.1f} minutes")
            return True
            
        except Exception as e:
            print(f"Failed to stop study mode: {e}")
            return False
    
    def _study_mode_monitor(self, duration_seconds: int):
        """Monitor study mode and provide updates"""
        start_time = time.time()
        
        while not self.stop_event.is_set() and (time.time() - start_time) < duration_seconds:
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            
            if remaining > 0:
                print(f"Study mode: {int(remaining//60)}:{int(remaining%60):02d} remaining")
                time.sleep(60)  # Update every minute
            else:
                break
        
        if not self.stop_event.is_set():
            print("Study mode completed!")
            self.stop_study_mode()
    
    def block_websites(self):
        """Block distracting websites by modifying hosts file"""
        try:
            hosts_file = CONFIG['scholar_pack']['study_mode'].get('hosts_file', 'C:/Windows/System32/drivers/etc/hosts')
            block_sites = CONFIG['scholar_pack']['study_mode']['block_sites']
            
            # Read current hosts file
            with open(hosts_file, 'r') as f:
                hosts_content = f.read()
            
            # Add block entries if not already present
            new_entries = []
            for site in block_sites:
                entry = f"127.0.0.1 {site}\n"
                if entry not in hosts_content:
                    new_entries.append(entry)
            
            if new_entries:
                with open(hosts_file, 'a') as f:
                    f.write("\n# JARVIS Study Mode Blocks\n")
                    f.writelines(new_entries)
                print(f"Blocked {len(new_entries)} websites")
                
        except Exception as e:
            print(f"Failed to block websites: {e}")
    
    def unblock_websites(self):
        """Unblock websites by removing JARVIS entries from hosts file"""
        try:
            hosts_file = CONFIG['scholar_pack']['study_mode'].get('hosts_file', 'C:/Windows/System32/drivers/etc/hosts')
            
            with open(hosts_file, 'r') as f:
                lines = f.readlines()
            
            # Remove JARVIS block entries
            filtered_lines = []
            in_jarvis_block = False
            for line in lines:
                if "# JARVIS Study Mode Blocks" in line:
                    in_jarvis_block = True
                    continue
                elif in_jarvis_block and line.strip() == "":
                    in_jarvis_block = False
                    continue
                
                if not in_jarvis_block:
                    filtered_lines.append(line)
            
            with open(hosts_file, 'w') as f:
                f.writelines(filtered_lines)
                
            print("Unblocked websites")
            
        except Exception as e:
            print(f"Failed to unblock websites: {e}")
    
    # FEATURE 7: AUTO-FLASHCARD GENERATION
    def generate_flashcards(self, topic: str, content: str) -> List[Dict]:
        """Generate flashcards from content"""
        if not CONFIG['scholar_pack']['auto_flashcard']['enabled']:
            return []
        
        try:
            # Simple flashcard generation (can be enhanced with AI)
            flashcards = []
            
            # Split content into sentences
            sentences = content.split('.')
            
            for i, sentence in enumerate(sentences[:20]):  # Limit to 20 cards
                sentence = sentence.strip()
                if len(sentence) > 10:  # Skip very short sentences
                    flashcard = {
                        'id': len(self.flashcards) + 1,
                        'front': f"What is the main point of: {sentence[:50]}...",
                        'back': sentence,
                        'topic': topic,
                        'created_at': datetime.now().isoformat()
                    }
                    flashcards.append(flashcard)
            
            self.flashcards.extend(flashcards)
            self.save_flashcards()
            
            self.log_study_event("FLASHCARDS_GENERATED", f"Generated {len(flashcards)} flashcards for topic: {topic}")
            return flashcards
            
        except Exception as e:
            print(f"Failed to generate flashcards: {e}")
            return []
    
    def save_flashcards(self):
        """Save flashcards to file"""
        try:
            output_dir = CONFIG['scholar_pack']['auto_flashcard'].get('output_dir', 'flashcards/')
            os.makedirs(output_dir, exist_ok=True)
            
            flashcard_file = os.path.join(output_dir, 'flashcards.json')
            with open(flashcard_file, 'w') as f:
                json.dump(self.flashcards, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save flashcards: {e}")
    
    # FEATURE 8: PROGRESS BAR
    def show_progress_bar(self, current: int, total: int, description: str = "Progress"):
        """Display a modern progress bar in terminal"""
        if not CONFIG['scholar_pack']['progress_bar']['enabled']:
            return
        
        try:
            percentage = (current / total) * 100
            bar_length = 40
            filled_length = int(bar_length * current // total)
            
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            
            print(f'\r{description}: |{bar}| {percentage:.1f}% ({current}/{total})', end='', flush=True)
            
            if current == total:
                print()  # New line when complete
                
        except Exception as e:
            print(f"Progress bar error: {e}")
    
    # FEATURE 9: NOTE TAKING
    def take_note(self, content: str, topic: str = "General") -> bool:
        """Take and save a note"""
        if not CONFIG['scholar_pack']['note_taking']['enabled']:
            return False
        
        try:
            note = {
                'id': len(self.notes) + 1,
                'content': content,
                'topic': topic,
                'created_at': datetime.now().isoformat()
            }
            
            self.notes.append(note)
            
            if CONFIG['scholar_pack']['note_taking']['auto_save']:
                self.save_notes()
            
            self.log_study_event("NOTE_TAKEN", f"Note added to topic: {topic}")
            return True
            
        except Exception as e:
            print(f"Failed to take note: {e}")
            return False
    
    def save_notes(self):
        """Save notes to file"""
        try:
            notes_file = f"notes_{datetime.now().strftime('%Y%m%d')}.md"
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(f"# JARVIS Notes - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                for note in self.notes:
                    f.write(f"## {note['topic']}\n")
                    f.write(f"{note['content']}\n")
                    f.write(f"*{note['created_at']}*\n\n")
                    
        except Exception as e:
            print(f"Failed to save notes: {e}")
    
    # FEATURE 10: RESEARCH ASSISTANT
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research a topic using available sources"""
        if not CONFIG['scholar_pack']['research_assistant']['enabled']:
            return {'error': 'Research assistant disabled'}
        
        try:
            results = {
                'topic': topic,
                'sources': [],
                'summary': '',
                'timestamp': datetime.now().isoformat()
            }
            
            # Wikipedia research
            if 'wikipedia' in CONFIG['scholar_pack']['research_assistant']['sources']:
                wiki_result = self._search_wikipedia(topic)
                if wiki_result:
                    results['sources'].append(wiki_result)
                    results['summary'] = wiki_result.get('summary', '')
            
            self.log_study_event("RESEARCH_PERFORMED", f"Researched topic: {topic}")
            return results
            
        except Exception as e:
            print(f"Research error: {e}")
            return {'error': str(e)}
    
    def _search_wikipedia(self, topic: str) -> Optional[Dict]:
        """Search Wikipedia for topic"""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'source': 'Wikipedia',
                    'title': data.get('title', topic),
                    'summary': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return None
    
    def get_study_stats(self) -> Dict[str, Any]:
        """Get current study statistics"""
        return {
            'study_mode_active': self.study_mode_active,
            'focus_duration': time.time() - self.focus_start_time if self.focus_start_time else 0,
            'total_flashcards': len(self.flashcards),
            'total_notes': len(self.notes),
            'last_activity': datetime.now().isoformat()
        }
    
    def log_study_event(self, event_type: str, details: str):
        """Log study events to Syllabus_Progress.md"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
## Study Event - {timestamp}

**Event:** {event_type}
**Details:** {details}

---
"""
            
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Failed to log study event: {e}")
