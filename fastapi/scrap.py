from apify_client import ApifyClient
from urllib.parse import urlparse
from datetime import datetime
from vectorStaxConnect import db  # Import the database connection from vectorStaxConnect
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the ApifyClient with your API token
apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def get_instagram_username(url):
    parsed_url = urlparse(url)
    username = parsed_url.path.strip('/').split('/')[0]
    return username

def delete_user_data(username):
    """Delete all data for a specific username"""
    try:
        instagram_collection = db.get_collection("instagram_data")
        instagram_collection.delete_many({"username": username})
        print(f"🗑️ Deleted previous data for username: {username}")
    except Exception as e:
        print(f"❌ Error deleting user data: {str(e)}")

def insert_post_to_astra(post_data):
    """Insert post data into Astra DB with status"""
    try:
        instagram_collection = db.get_collection("instagram_data")
        # Add a type field to identify this as a post
        post_data['data_type'] = 'post'
        instagram_collection.insert_one(post_data)
        return True, "Post data inserted successfully"
    except Exception as e:
        return False, f"Error inserting post data: {str(e)}"

def insert_profile_to_astra(profile_data):
    """Insert profile data into Astra DB"""
    try:
        instagram_collection = db.get_collection("instagram_data")
        profile_data['data_type'] = 'profile'
        instagram_collection.delete_many({
            "username": profile_data['username'],
            "data_type": "profile"
        })

        # Insert new profile data
        instagram_collection.insert_one(profile_data)
        return True, "Profile data inserted successfully"
    except Exception as e:
        return False, f"Error inserting profile data: {str(e)}"

def print_post_details(post_data):
    print("="*50)
    print(f"Post Details:")
    print("="*50)
    print(f"Username: {post_data['username']}")
    print(f"Post ID: {post_data['post_id']}")
    print(f"Type: {post_data['post_type']}")
    print(f"Likes: {post_data['likes']:,}")
    print(f"Comments: {post_data['comments']:,}")
    print(f"Shares: {post_data['shares']:,}")
    
    # Add video-specific details if post is a video
    if post_data['post_type'].lower() == 'video':
        print(f"Video Views: {post_data.get('video_views', 0):,}")
        duration = post_data.get('video_duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        print(f"Video Duration: {minutes}m {seconds}s")
    
    print(f"Posted at: {post_data['timestamp']}")
    print(f"URL: {post_data['profile_url']}")
    print(f"Caption: {post_data['caption'][:100]}..." if post_data['caption'] else "Caption: None")
    print("-"*50)

def print_profile_details(profile):
    """Print formatted profile details"""
    print("\n📱 Profile Details:")
    print(f"👤 Username: {profile['username']}")
    print(f"📝 Full Name: {profile['full_name']}")
    print(f"📖 Bio: {profile['biography']}")
    print(f"👥 Followers: {profile['followers_count']}")
    print(f"👥 Following: {profile['following_count']}")
    print(f"✅ Verified: {profile['is_verified']}")
    print(f"🔗 Profile URL: {profile['profile_url']}")
    print(f"🖼️ Profile Picture: {profile['profile_pic_url']}")
    print(f"🔗 External URL: {profile['external_url']}")
    print(f"💼 Business Category: {profile['business_category']}\n")

def insert_data_to_astra(profile_data, posts_data):
    """Insert both profile and posts data as a single nested document"""
    try:
        instagram_collection = db.get_collection("instagram_data")
        
        # Create the nested structure with numbered posts
        numbered_posts = {}
        for idx, post in enumerate(posts_data, 1):  # Start counting from 1
            numbered_posts[f"post_{idx}"] = post['post_data']
        
        document = {
            "username": profile_data['username'],
            "profile_data": profile_data,
            "posts": numbered_posts,
            "last_updated": datetime.now().isoformat()
        }
        
        # Delete existing data for this username only
        instagram_collection.delete_many({"username": profile_data['username']})
        print(f"🗑️ Cleared existing data for username: {profile_data['username']}")
        
        # Insert the new nested document
        instagram_collection.insert_one(document)
        return True, "Data inserted successfully"
    except Exception as e:
        return False, f"Error inserting data: {str(e)}"

def scrape_instagram_profile(username: str, results_limit: int = 5):
    """
    Scrape Instagram profile and posts data, store in database and return results
    """
    try:
        # Ensure results_limit is an integer and print for debugging
        results_limit = int(results_limit)
        print(f"🎯 Requested {results_limit} posts")
        
        # Initialize return data
        result = {
            'profile_data': None,
            'posts_data': [],
            'success': False,
            'error': None
        }

        try:
            # First, clear ALL existing data from collection
            instagram_collection = db.get_collection("instagram_data")
            instagram_collection.delete_many({})
            print("🗑️ Cleared all existing data from database")

            # Configure input for user details
            input_data = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsType": "details",
                "searchType": "user",
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"]
                },
                "languageCode": "en"
            }

            print(f"🔄 Starting Instagram scraper for {username}...")
            print(f"📊 Attempting to fetch {results_limit} posts...")

            # Get user details
            actor_call = apify_client.actor('apify/instagram-scraper').call(
                run_input=input_data,
                timeout_secs=120
            )
            
            profile_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items

            if not profile_items:
                raise Exception("No profile data found")

            # Get profile data
            profile_item = profile_items[0]
            
            if 'error' in profile_item:
                raise Exception("Error in profile data")

            # Process profile data
            profile_data = {
                'username': profile_item.get('username', username),
                'full_name': profile_item.get('fullName', ''),
                'biography': profile_item.get('biography', ''),
                'followers_count': profile_item.get('followersCount', 0),
                'following_count': profile_item.get('followsCount', 0),
                'is_verified': profile_item.get('verified', False),
                'profile_pic_url': profile_item.get('profilePicUrl', ''),
                'profile_url': f"https://www.instagram.com/{username}/",
                'external_url': profile_item.get('externalUrl', ''),
                'business_category': profile_item.get('businessCategoryName', ''),
                'total_posts': profile_item.get('postsCount', 0)
            }

            result['profile_data'] = profile_data

            # Update the posts scraping configuration
            input_data.update({
                "resultsType": "posts",
                "maxItems": results_limit,  # Set the maximum items to fetch
                "searchType": "user",
                "searchLimit": results_limit,  # Set the search limit
                "extendOutputFunction": """async ({ data, item, page, customData }) => {
                    return item;
                }""",
                "scrapeStories": False,
                "scrapeHighlights": False,
                "scrapeIgtv": False,
                "scrapeReels": True,
                "scrapePosts": True,
                "scrapeComments": False,
                "sort": "newest",
                "limit": results_limit  # Add an explicit limit
            })

            # Increase timeout for larger number of posts
            actor_call = apify_client.actor('apify/instagram-scraper').call(
                run_input=input_data,
                timeout_secs=300  # Increased timeout to 5 minutes for more posts
            )
            
            posts_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items
            posts_items = sorted(posts_items, key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Make sure we get the requested number of posts
            if len(posts_items) < results_limit:
                print(f"⚠️ Warning: Only found {len(posts_items)} posts, less than requested {results_limit}")
            
            # Process all fetched posts
            result['posts_data'] = []
            for idx, item in enumerate(posts_items[:results_limit], 1):
                if 'error' in item:
                    continue
                    
                video_duration = int(round(item.get('videoDuration', 0))) if isinstance(item.get('videoDuration'), float) else 0
                
                post_data = {
                    'post_number': f"post_{idx}",  # Add post number
                    'username': username,
                    'post_id': item.get('id', 'unknown'),
                    'post_type': item.get('type', 'unknown'),
                    'likes': item.get('likesCount', 0),
                    'comments': item.get('commentsCount', 0),
                    'shares': item.get('sharesCount', 0),
                    'timestamp': item.get('timestamp', 'unknown'),
                    'profile_url': item.get('url', ''),
                    'caption': item.get('caption', ''),
                    'video_views': item.get('videoViewCount', 0) if item.get('type', '').lower() == 'video' else 0,
                    'video_duration': video_duration if item.get('type', '').lower() == 'video' else 0
                }
                
                result['posts_data'].append({
                    'post_id': post_data['post_id'],
                    'post_data': post_data,
                    'post_number': f"post_{idx}",  # Add post number to response
                    'db_insert_status': True,
                    'insert_message': 'Post data ready'
                })

            # Store both profile and posts data together
            db_success, db_message = insert_data_to_astra(profile_data, result['posts_data'])
            result['db_status'] = db_success
            result['db_message'] = db_message

            result['success'] = True
            print(f"✅ Successfully fetched {len(result['posts_data'])} posts")

            return result

        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error processing data: {str(e)}")
            return result

    except Exception as e:
        return {
            'profile_data': None,
            'posts_data': [],
            'success': False,
            'error': f"Failed to process data: {str(e)}"
        }

if __name__ == "__main__":
    
    # Test Function Calling 
    # Test username
    test_username = "cristiano"  # or any other Instagram username you want to test
    print(f"🚀 Starting scrape for username: {test_username}")
    
    # Call the scraping function
    result = scrape_instagram_profile(test_username, results_limit=5)

    
    
    # Print results
    if result['success']:
        print("\n✅ Scraping completed successfully!")
        
        # Print profile details
        if result['profile_data']:
            print_profile_details(result['profile_data'])
        
        # Print post details
        print(f"\nFetched {len(result['posts_data'])} posts:")
        for post in result['posts_data']:
            print_post_details(post['post_data'])
    else:
        print(f"\n❌ Scraping failed: {result['error']}")