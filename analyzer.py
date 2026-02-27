import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter, defaultdict
import re
import nltk
from nltk.corpus import stopwords
from typing import List, Dict, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

class QuestionTrendAnalyzer:
    def __init__(self, similarity_threshold=0.7):
        self.similarity_threshold = similarity_threshold
        try:
            self.stop_words = stopwords.words('english')
        except:
            nltk.download('stopwords')
            self.stop_words = stopwords.words('english')
        
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=500,
            min_df=1
        )
        
        # Subject-specific keywords for better topic extraction
        self.topics_database = {
            # OOP Topics
            'Class': ['class', 'object', 'constructor', 'instance', 'new', 'this', 'super'],
            'Inheritance': ['inheritance', 'extends', 'subclass', 'parent', 'child', 'derived'],
            'Polymorphism': ['polymorphism', 'overloading', 'overriding', 'dynamic dispatch'],
            'Encapsulation': ['encapsulation', 'access modifier', 'private', 'public', 'protected'],
            'Abstraction': ['abstract', 'interface', 'implements'],
            'Exception': ['exception', 'try', 'catch', 'throw', 'finally', 'error'],
            'Thread': ['thread', 'runnable', 'multithreading', 'synchronized', 'wait', 'notify'],
            'String': ['string', 'stringbuffer', 'stringbuilder', 'immutable'],
            'Package': ['package', 'import', 'namespace'],
            'Collection': ['collection', 'list', 'arraylist', 'hashmap', 'set', 'iterator'],
            'File I/O': ['file', 'stream', 'input', 'output', 'reader', 'writer'],
            
            # Data Structures Topics
            'Array': ['array', 'matrix', 'multidimensional'],
            'LinkedList': ['linked list', 'singly', 'doubly', 'circular', 'node'],
            'Stack': ['stack', 'push', 'pop', 'peek', 'lifo'],
            'Queue': ['queue', 'enqueue', 'dequeue', 'circular queue', 'priority queue'],
            'Tree': ['tree', 'binary', 'bst', 'avl', 'traversal', 'inorder', 'preorder', 'postorder'],
            'Graph': ['graph', 'dfs', 'bfs', 'dijkstra', 'prim', 'kruskal', 'topological'],
            'Sorting': ['sort', 'bubble', 'merge', 'quick', 'heap', 'insertion', 'selection'],
            'Searching': ['search', 'linear', 'binary', 'sequential'],
            'Hashing': ['hash', 'hashing', 'collision', 'chaining', 'probing', 'table'],
            'Heap': ['heap', 'min-heap', 'max-heap', 'priority queue']
        }
        
    def preprocess_question(self, question_text: str) -> str:
        """Clean and preprocess question text"""
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', question_text.lower())
        # Remove extra spaces
        text = ' '.join(text.split())
        return text
    
    def extract_keywords(self, question_text: str) -> List[str]:
        """Extract important keywords from question"""
        words = question_text.lower().split()
        # Remove common words
        keywords = [w for w in words if len(w) > 3 and w not in self.stop_words]
        return keywords
    
    def find_similar_questions(self, questions: List[Dict]) -> List[List[int]]:
        """Group similar questions using TF-IDF"""
        if len(questions) < 2:
            return [[i] for i in range(len(questions))]
        
        # Preprocess questions
        processed = [self.preprocess_question(q['text']) for q in questions]
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(processed)
            
            # Calculate similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Group similar questions
            groups = []
            used = set()
            
            for i in range(len(questions)):
                if i in used:
                    continue
                    
                group = [i]
                for j in range(i + 1, len(questions)):
                    if j not in used and similarity_matrix[i][j] > self.similarity_threshold:
                        group.append(j)
                        used.add(j)
                
                groups.append(group)
                used.add(i)
            
            return groups
            
        except Exception as e:
            print(f"Error in similarity: {e}")
            return [[i] for i in range(len(questions))]
    
    def extract_topics(self, question_text: str) -> List[str]:
        """Extract topics from question text"""
        text_lower = question_text.lower()
        found_topics = []
        
        for topic, keywords in self.topics_database.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_topics.append(topic)
                    break
        
        return list(set(found_topics))  # Remove duplicates
    
    def analyze_patterns(self, questions: List[Dict]) -> Dict:
        """Analyze question patterns"""
        patterns = {
            'explain': 0,
            'define': 0,
            'what': 0,
            'difference': 0,
            'compare': 0,
            'write': 0,
            'list': 0,
            'state': 0,
            'discuss': 0,
            'derive': 0,
            'how': 0,
            'why': 0
        }
        
        for q in questions:
            text = q['text'].lower()
            for pattern in patterns.keys():
                if pattern in text:
                    patterns[pattern] += 1
        
        # Remove zero counts
        return {k: v for k, v in patterns.items() if v > 0}
    
    def calculate_frequencies(self, question_groups: List[List[int]], 
                            questions: List[Dict]) -> Dict:
        """Calculate question and topic frequencies"""
        result = {
            'question_clusters': [],
            'topic_frequency': Counter(),
            'year_distribution': defaultdict(list)
        }
        
        for group in question_groups:
            cluster_questions = [questions[i] for i in group]
            
            # Get all texts in cluster
            cluster_texts = [q['text'] for q in cluster_questions]
            
            # Extract topics from cluster
            all_topics = []
            for q in cluster_questions:
                topics = self.extract_topics(q['text'])
                all_topics.extend(topics)
            
            # Count topic frequency
            topic_counter = Counter(all_topics)
            for topic, count in topic_counter.items():
                result['topic_frequency'][topic] += count
            
            # Create cluster info
            result['question_clusters'].append({
                'questions': cluster_texts[:3],  # First 3 questions as sample
                'count': len(cluster_questions),
                'frequency': len(cluster_questions),  # How many times appeared
                'main_topics': [t for t, c in topic_counter.most_common(2)],
                'sample_question': cluster_texts[0][:150] + '...' if len(cluster_texts[0]) > 150 else cluster_texts[0]
            })
        
        # Sort by frequency (most repeated first)
        result['question_clusters'].sort(key=lambda x: x['frequency'], reverse=True)
        
        return result
    
    def generate_revision_plan(self, frequencies: Dict, patterns: Dict) -> Dict:
        """Generate prioritized revision plan"""
        clusters = frequencies['question_clusters']
        topic_freq = frequencies['topic_frequency']
        
        # Categorize by importance
        super_repeaters = []
        hot_topics = []
        occasional = []
        
        for cluster in clusters:
            if cluster['frequency'] >= 3:
                super_repeaters.append(cluster)
            elif cluster['frequency'] == 2:
                hot_topics.append(cluster)
            else:
                occasional.append(cluster)
        
        # Get top topics
        top_topics = topic_freq.most_common(5)
        
        # Determine main question type
        main_pattern = max(patterns, key=patterns.get) if patterns else 'explain'
        
        # Create hourly plan
        hourly_plan = []
        
        if super_repeaters:
            hourly_plan.append(f"Hour 1-2: MASTER {len(super_repeaters)} SUPER REPEATER TOPICS - These appear every year!")
            for i, cluster in enumerate(super_repeaters[:3]):  # Show top 3
                topics = ', '.join(cluster['main_topics']) if cluster['main_topics'] else 'Important'
                hourly_plan.append(f"  • Topic {i+1}: {topics}")
        
        if hot_topics:
            hourly_plan.append(f"Hour 3-4: FOCUS on {len(hot_topics)} HOT TOPICS - High probability")
            for i, cluster in enumerate(hot_topics[:3]):
                topics = ', '.join(cluster['main_topics']) if cluster['main_topics'] else 'Key concept'
                hourly_plan.append(f"  • {topics}")
        
        if top_topics:
            hourly_plan.append(f"Hour 5: REVIEW CORE CONCEPTS - {', '.join([t[0] for t in top_topics[:3]])}")
        
        hourly_plan.append(f"Hour 6: PRACTICE '{main_pattern.upper()}' type questions - Most common pattern")
        
        # Create summary
        summary = {
            'total_questions': sum(c['count'] for c in clusters),
            'unique_topics': len(topic_freq),
            'repeated_questions': len(super_repeaters) + len(hot_topics)
        }
        
        return {
            'summary': summary,
            'super_repeaters': super_repeaters[:5],  # Top 5
            'hot_topics': hot_topics[:5],  # Top 5
            'occasional': occasional[:5],
            'top_topics': top_topics,
            'question_patterns': patterns,
            'main_pattern': main_pattern,
            'hourly_plan': hourly_plan
        }
    
    def generate_charts(self, frequencies: Dict, patterns: Dict) -> Dict:
        """Generate charts for visualization"""
        charts = {}
        
        try:
            # Topic frequency chart
            if frequencies['topic_frequency']:
                plt.figure(figsize=(10, 6))
                topics = list(frequencies['topic_frequency'].keys())[:8]
                counts = list(frequencies['topic_frequency'].values())[:8]
                
                plt.barh(range(len(topics)), counts, color='#6366f1')
                plt.yticks(range(len(topics)), topics)
                plt.xlabel('Frequency')
                plt.title('Most Common Topics')
                plt.tight_layout()
                
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                charts['topic_chart'] = base64.b64encode(img.getvalue()).decode()
                plt.close()
            
            # Patterns chart
            if patterns:
                plt.figure(figsize=(8, 8))
                colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                plt.pie(patterns.values(), labels=patterns.keys(), autopct='%1.1f%%', colors=colors)
                plt.title('Question Pattern Distribution')
                plt.tight_layout()
                
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                charts['pattern_chart'] = base64.b64encode(img.getvalue()).decode()
                plt.close()
                
        except Exception as e:
            print(f"Chart error: {e}")
            
        return charts
    
    def analyze(self, questions: List[Dict]) -> Dict:
        """Main analysis method"""
        if not questions:
            return {}
        
        print(f"🔍 Analyzing {len(questions)} questions...")
        
        # Find similar questions
        question_groups = self.find_similar_questions(questions)
        print(f"📊 Found {len(question_groups)} question clusters")
        
        # Calculate frequencies
        frequencies = self.calculate_frequencies(question_groups, questions)
        
        # Analyze patterns
        patterns = self.analyze_patterns(questions)
        
        # Generate revision plan
        revision_plan = self.generate_revision_plan(frequencies, patterns)
        
        # Generate charts
        charts = self.generate_charts(frequencies, patterns)
        
        return {
            'summary': revision_plan['summary'],
            'frequencies': frequencies,
            'patterns': patterns,
            'revision_plan': revision_plan,
            'charts': charts
        }