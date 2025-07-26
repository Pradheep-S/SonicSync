import logging
import re
import os
import numpy as np

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered matching and enhancement"""
    
    def __init__(self):
        self.model = None
        self.openai_client = None
        
        # Initialize sentence transformer with better error handling
        try:
            logger.info("Loading AI model...")
            # Set environment variables to avoid warnings
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            
            # Import sentence transformers with fallback
            try:
                # Try to import without causing huggingface_hub issues
                import sentence_transformers
                from sentence_transformers import SentenceTransformer, util
                
                # Initialize model with explicit cache handling
                self.model = SentenceTransformer('all-MiniLM-L6-v2', 
                                               cache_folder=os.path.expanduser('~/.cache/torch/sentence_transformers'))
                self.util = util
                logger.info("✅ AI model loaded successfully")
            except Exception as import_err:
                logger.warning(f"SentenceTransformers initialization failed: {import_err}")
                logger.info("AI features will use fallback methods")
                self.model = None
                self.util = None
        except Exception as e:
            logger.error(f"❌ Failed to load AI model: {str(e)}")
            logger.info("AI features will use fallback methods")
            self.model = None
            self.util = None
        
        # Initialize OpenAI (optional)
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_key != 'your_openai_api_key_here':
                import openai
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            else:
                logger.info("OpenAI API key not configured - advanced AI features disabled")
        except ImportError as e:
            logger.warning(f"OpenAI not available: {str(e)}")
            self.openai_client = None
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {str(e)}")
            self.openai_client = None
    
    def get_best_match(self, query, candidates):
        """Find the best matching candidate using semantic similarity"""
        try:
            if not self.model or not candidates:
                return candidates[0] if candidates else None
            
            # Extract titles from candidate objects if they're dictionaries
            candidate_texts = []
            for candidate in candidates:
                if isinstance(candidate, dict):
                    candidate_texts.append(candidate.get('title', str(candidate)))
                else:
                    candidate_texts.append(str(candidate))
            
            if not candidate_texts:
                return None
            
            # Encode query and candidates
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            candidate_embeddings = self.model.encode(candidate_texts, convert_to_tensor=True)
            
            # Calculate cosine similarities
            if self.util:
                similarities = self.util.cos_sim(query_embedding, candidate_embeddings)[0]
            else:
                # Fallback to manual cosine similarity calculation
                import torch
                similarities = torch.nn.functional.cosine_similarity(
                    query_embedding.unsqueeze(0), candidate_embeddings, dim=1
                )
            
            # Find the best match
            best_idx = similarities.argmax().item()
            best_score = similarities[best_idx].item()
            
            logger.info(f"Best match found with similarity score: {best_score:.3f}")
            
            # Return the original candidate object
            return candidates[best_idx]
            
        except Exception as e:
            logger.error(f"Error finding best match: {str(e)}")
            # Fallback to simple string matching
            return self._fallback_string_match(query, candidates)
    
    def _fallback_string_match(self, query, candidates):
        """Fallback method using simple string matching"""
        try:
            query_lower = query.lower()
            best_match = None
            best_score = 0
            
            for candidate in candidates:
                if isinstance(candidate, dict):
                    text = candidate.get('title', str(candidate)).lower()
                else:
                    text = str(candidate).lower()
                
                # Simple word overlap scoring
                query_words = set(query_lower.split())
                text_words = set(text.split())
                overlap = len(query_words.intersection(text_words))
                score = overlap / len(query_words) if query_words else 0
                
                if score > best_score:
                    best_score = score
                    best_match = candidate
            
            return best_match
            
        except Exception as e:
            logger.error(f"Fallback matching failed: {str(e)}")
            return candidates[0] if candidates else None
    
    def enhance_search_query(self, original_query):
        """Enhance search query by cleaning and optimizing it"""
        try:
            # First try OpenAI enhancement if available
            if self.openai_client:
                enhanced = self._enhance_with_openai(original_query)
                if enhanced:
                    return enhanced
            
            # Fallback to rule-based enhancement
            return self._enhance_with_rules(original_query)
            
        except Exception as e:
            logger.error(f"Error enhancing query: {str(e)}")
            return original_query
    
    def _enhance_with_openai(self, query):
        """Enhance query using OpenAI"""
        try:
            prompt = f"""Clean and simplify this song title for better search results:
            
Title: "{query}"

Instructions:
- Remove brackets, parentheses, and their content
- Remove words like "feat", "featuring", "remix", "original soundtrack", "OST"
- Keep only the main song name and artist
- Make it simple and searchable
- Return only the cleaned title, nothing else

Cleaned title:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            enhanced = response.choices[0].message.content.strip()
            logger.info(f"OpenAI enhanced: '{query}' -> '{enhanced}'")
            return enhanced
            
        except Exception as e:
            logger.warning(f"OpenAI enhancement failed: {str(e)}")
            return None
    
    def _enhance_with_rules(self, original_query):
        """Rule-based query enhancement"""
        try:
            # Remove brackets and parentheses content
            query = re.sub(r'\[.*?\]|\(.*?\)', '', original_query)
            
            # Remove common music-related keywords that might hurt search
            keywords_to_remove = [
                'original soundtrack', 'ost', 'feat', 'featuring', 'ft',
                'remix', 'version', 'remastered', 'deluxe', 'bonus',
                'single', 'album', 'ep', 'lp', 'official', 'music video',
                'lyric video', 'audio', 'hd', 'hq'
            ]
            
            query_lower = query.lower()
            for keyword in keywords_to_remove:
                query_lower = query_lower.replace(keyword, ' ')
            
            # Clean up extra spaces and special characters
            query = re.sub(r'[^\w\s]', ' ', query_lower)
            query = ' '.join(query.split())
            
            # Extract main song name and artist
            parts = query.split(' by ')
            if len(parts) == 2:
                song_name, artist = parts
                enhanced_query = f"{song_name.strip()} {artist.strip()}"
            else:
                enhanced_query = query
            
            logger.info(f"Rule-based enhanced: '{original_query}' -> '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Rule-based enhancement failed: {str(e)}")
            return original_query
    
    def analyze_playlist_mood(self, tracks):
        """Analyze the mood of a playlist based on track names and artists"""
        try:
            if not tracks:
                return {"mood": "unknown", "confidence": 0.0}
            
            # Combine all track information
            playlist_text = " ".join([
                f"{track['name']} {track['artist']}" 
                for track in tracks[:20]  # Limit to first 20 for performance
            ])
            
            # Define mood keywords
            mood_keywords = {
                "energetic": ["dance", "party", "energy", "pump", "power", "rock", "metal", "beat"],
                "romantic": ["love", "heart", "kiss", "romantic", "valentine", "baby", "darling"],
                "sad": ["sad", "cry", "tears", "alone", "miss", "goodbye", "sorry", "hurt"],
                "peaceful": ["calm", "peace", "quiet", "soft", "gentle", "relax", "meditation"],
                "happy": ["happy", "joy", "smile", "sunshine", "celebration", "fun", "good"],
                "nostalgic": ["memory", "remember", "old", "past", "childhood", "yesterday"]
            }
            
            mood_scores = {}
            playlist_lower = playlist_text.lower()
            
            for mood, keywords in mood_keywords.items():
                score = sum(1 for keyword in keywords if keyword in playlist_lower)
                mood_scores[mood] = score
            
            # Find dominant mood
            if mood_scores:
                dominant_mood = max(mood_scores, key=mood_scores.get)
                max_score = mood_scores[dominant_mood]
                confidence = min(max_score / len(tracks), 1.0)
            else:
                dominant_mood = "mixed"
                confidence = 0.5
            
            return {
                "mood": dominant_mood,
                "confidence": confidence,
                "mood_breakdown": mood_scores,
                "description": self._get_mood_description(dominant_mood, confidence)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing playlist mood: {str(e)}")
            return {"mood": "unknown", "confidence": 0.0, "error": str(e)}
    
    def _get_mood_description(self, mood, confidence):
        """Get a human-readable description of the playlist mood"""
        descriptions = {
            "energetic": "This playlist is full of high-energy tracks perfect for workouts or parties!",
            "romantic": "A lovely collection of romantic songs perfect for special moments.",
            "sad": "A melancholic playlist that captures deep emotions and feelings.",
            "peaceful": "A calming collection ideal for relaxation and meditation.",
            "happy": "An uplifting playlist that's sure to brighten your day!",
            "nostalgic": "A trip down memory lane with songs that evoke the past.",
            "mixed": "A diverse playlist with a variety of moods and styles."
        }
        
        description = descriptions.get(mood, "An interesting collection of songs.")
        
        if confidence > 0.7:
            description += " The mood is very consistent throughout."
        elif confidence > 0.4:
            description += " The mood is fairly consistent."
        else:
            description += " The playlist has a varied emotional range."
        
        return description
    
    def suggest_similar_tracks(self, track_name, artist_name):
        """Suggest similar tracks (placeholder for future enhancement)"""
        try:
            # This is a placeholder for future AI-powered recommendations
            # Could integrate with Last.fm API, Spotify recommendations, etc.
            
            suggestions = [
                f"Similar to {track_name} by {artist_name}",
                "Consider checking related artists",
                "Look for songs in the same genre"
            ]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting similar tracks: {str(e)}")
            return []
    
    def generate_alternative_queries(self, original_query):
        """Generate alternative search queries for better matching"""
        try:
            alternatives = [original_query]
            
            # Try different variations
            # Remove artist name and keep only song
            parts = original_query.split(' by ')
            if len(parts) == 2:
                song_only = parts[0].strip()
                alternatives.append(song_only)
            
            # Try with common variations
            variations = [
                original_query.replace(' and ', ' & '),
                original_query.replace(' & ', ' and '),
                original_query.replace('\'', ''),
                re.sub(r'\s+', ' ', original_query)
            ]
            
            alternatives.extend(variations)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_alternatives = []
            for alt in alternatives:
                if alt.strip() and alt.strip() not in seen:
                    seen.add(alt.strip())
                    unique_alternatives.append(alt.strip())
            
            return unique_alternatives[:5]  # Limit to 5 alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternatives: {str(e)}")
            return [original_query]
    
    def score_search_results(self, query, results):
        """Score and rank search results based on relevance"""
        try:
            if not results or not self.model:
                return results
            
            # Get embeddings for query and results
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            
            scored_results = []
            for result in results:
                result_text = result.get('title', str(result)) if isinstance(result, dict) else str(result)
                result_embedding = self.model.encode(result_text, convert_to_tensor=True)
                
                # Calculate similarity
                if self.util:
                    similarity = self.util.cos_sim(query_embedding, result_embedding)[0][0].item()
                else:
                    # Fallback similarity calculation
                    try:
                        import torch
                        similarity = torch.nn.functional.cosine_similarity(
                            query_embedding.unsqueeze(0), result_embedding.unsqueeze(0), dim=1
                        )[0].item()
                    except:
                        # Ultimate fallback - simple text matching
                        similarity = 0.5
                
                # Add score to result
                if isinstance(result, dict):
                    result['ai_score'] = similarity
                    scored_results.append(result)
                else:
                    scored_results.append({'title': result_text, 'ai_score': similarity})
            
            # Sort by score descending
            scored_results.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
            
            return scored_results
            
        except Exception as e:
            logger.error(f"Error scoring results: {str(e)}")
            return results
