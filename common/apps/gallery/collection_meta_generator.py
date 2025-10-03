from typing import List, Dict, Any
from collections import Counter

def aggregate_collection_metadata(image_metadatas: List[Dict[str, Any]]) -> Dict[str, Any]:
    tags = []
    mood_tags = []
    for meta in image_metadatas:
        if not meta:
            continue
        tags.extend(meta.get('tags', []))
        mood_tags.extend(meta.get('mood_tags', []))
    tag_counts = Counter(tags)
    mood_counts = Counter(mood_tags)
    return {
        'tags': list(set(tags)),
        'mood_tags': list(set(mood_tags)),
        'image_count': len(image_metadatas),
        'top_tags': dict(tag_counts.most_common(10)),
        'top_moods': dict(mood_counts.most_common(5)),
    } 