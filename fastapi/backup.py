from apify_client import ApifyClient
from urllib.parse import urlparse
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime

# Initialize the ApifyClient with your API token
apify_client = ApifyClient('apify_api_KzmKE3wuJeT7jacl4mceqjwJGkfYCS0CFPIg')

def get_instagram_username(url):
    parsed_url = urlparse(url)
    username = parsed_url.path.strip('/').split('/')[0]
    return username

# Database configuration
client_id = 'EeouaCamaMPvmqYYxuaqgHFP'
client_secret = 'yRZMXchZZINKW4W2DAuiujErkhKDzsw0wbTTzk91LQsiMGPe.n4jwLuf+T-I4WwhRIQODhb+Ec3B_KqiLFKuDd+3tgLagCqY6fvjx8SQQxoWKeZR,LA-fNCktPgDNncn'
keyspace = 'social_media'

def delete_user_data(session, username):
    """Delete all data for a specific username"""
    delete_query = """
    DELETE FROM instagram_data WHERE username = %s
    """
    try:
        session.execute(delete_query, (username,))
        print(f"🗑️ Deleted previous data for username: {username}")
    except Exception as e:
        print(f"❌ Error deleting user data: {str(e)}")

def drop_and_create_table(session, username):
    """Drop existing table and create a new one"""
    # First drop the existing table
    drop_table_query = """
    DROP TABLE IF EXISTS instagram_data;
    """
    try:
        session.execute(drop_table_query)
        print(f"🗑️ Dropped existing table for username: {username}")
    except Exception as e:
        print(f"❌ Error dropping table: {str(e)}")

    # Create new table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS instagram_data (
        username text,
        post_id text,
        post_type text,
        likes int,
        comments int,
        shares int,
        timestamp text,
        profile_url text,
        caption text,
        PRIMARY KEY ((username), post_id)
    );
    """
    session.execute(create_table_query)
    print("✅ New table created successfully.\n")

def insert_post_to_astra(session, post_data):
    query = """
    INSERT INTO instagram_data (
        username, 
        post_id, 
        post_type, 
        likes, 
        comments, 
        shares, 
        timestamp, 
        profile_url, 
        caption,
        video_views,
        video_duration
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        session.execute(query, (
            post_data['username'],
            post_data['post_id'],
            post_data['post_type'],
            post_data['likes'],
            post_data['comments'],
            post_data['shares'],
            post_data['timestamp'],
            post_data['profile_url'],
            post_data['caption'],
            post_data.get('video_views', 0),
            post_data.get('video_duration', 0)
        ))
        print(f"✅ Data inserted successfully for post ID: {post_data['post_id']}\n")
    except Exception as e:
        print(f"❌ Error inserting data: {str(e)}")

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

def fetch_instagram_data(username, session, results_limit=2):
    try:
        # Drop and recreate tables
        drop_and_create_profile_table(session)
        drop_and_create_posts_table(session)

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
        
        # Get user details
        actor_call = apify_client.actor('apify/instagram-scraper').call(
            run_input=input_data,
            timeout_secs=120
        )
        
        print("📥 Fetching profile data...")
        profile_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items

        if not profile_items:
            print("❌ No profile data found.")
            return

        # Get profile data from the first item
        profile_item = profile_items[0]
        
        if not profile_item or 'error' in profile_item:
            print("❌ Error in profile data")
            return

        # Insert profile data
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
            'business_category': profile_item.get('businessCategoryName', '')
        }

        insert_profile_to_astra(session, profile_data)
        print_profile_details(profile_data)

        # Now get posts with a separate call
        input_data.update({
            "resultsType": "posts",
            "maxItems": results_limit,
            "searchType": "user",
            "searchLimit": results_limit,
            "extendOutputFunction": """async ({ data, item, page, customData }) => {
                return item;
            }""",
            "scrapeStories": False,
            "scrapeHighlights": False,
            "scrapeIgtv": False,
            "scrapeReels": True,
            "scrapePosts": True,
            "scrapeComments": False,
            "sort": "newest"
        })

        actor_call = apify_client.actor('apify/instagram-scraper').call(
            run_input=input_data,
            timeout_secs=120
        )
        
        print("\n📥 Fetching posts data...")
        posts_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items

        if not posts_items:
            print("❌ No posts found.")
            return

        # Sort posts by timestamp before processing
        posts_items = list(posts_items)
        posts_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)  # Sort newest first
        posts_items = posts_items[:results_limit]  # Take only the required number of posts
        print(f"\n📊 Processing {len(posts_items)} posts\n")

        for item in posts_items:
            if 'error' in item:
                continue
                
            # Convert video duration to total seconds as integer
            video_duration = item.get('videoDuration', 0)
            if isinstance(video_duration, float):
                video_duration = int(round(video_duration))  # Round to nearest second
            
            post_data = {
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
            print_post_details(post_data)
            insert_post_to_astra(session, post_data)

    except Exception as e:
        print(f"❌ Error fetching data for {username}: {str(e)}")
        raise

def drop_and_create_profile_table(session):
    """Drop existing profile table and create a new one"""
    drop_table_query = "DROP TABLE IF EXISTS instagram_profile;"
    create_table_query = """
    CREATE TABLE IF NOT EXISTS instagram_profile (
        username text PRIMARY KEY,
        full_name text,
        biography text,
        followers_count int,
        following_count int,
        is_verified boolean,
        profile_pic_url text,
        profile_url text,
        external_url text,
        business_category text
    );
    """
    try:
        session.execute(drop_table_query)
        session.execute(create_table_query)
        print("✅ Profile table created successfully")
    except Exception as e:
        print(f"❌ Error creating profile table: {str(e)}")

def insert_profile_to_astra(session, profile_data):
    """Insert profile data into Astra DB"""
    insert_query = """
    INSERT INTO instagram_profile (
        username, full_name, biography, followers_count, following_count,
        is_verified, profile_pic_url, profile_url, external_url, business_category
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        session.execute(insert_query, (
            profile_data['username'],
            profile_data['full_name'],
            profile_data['biography'],
            profile_data['followers_count'],
            profile_data['following_count'],
            profile_data['is_verified'],
            profile_data['profile_pic_url'],
            profile_data['profile_url'],
            profile_data['external_url'],
            profile_data['business_category']
        ))
        print("✅ Profile data inserted successfully")
    except Exception as e:
        print(f"❌ Error inserting profile data: {str(e)}")

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

def drop_and_create_posts_table(session):
    """Drop existing posts table and create a new one"""
    drop_table_query = "DROP TABLE IF EXISTS instagram_data;"
    create_table_query = """
    CREATE TABLE IF NOT EXISTS instagram_data (
        username text,
        post_id text,
        post_type text,
        likes int,
        comments int,
        shares int,
        timestamp text,
        profile_url text,
        caption text,
        video_views int,
        video_duration int,
        PRIMARY KEY (username, post_id)
    );
    """
    try:
        session.execute(drop_table_query)
        session.execute(create_table_query)
        print("✅ Posts table created successfully")
    except Exception as e:
        print(f"❌ Error creating posts table: {str(e)}")

def main():
    try:
        # Connect to database
        auth_provider = PlainTextAuthProvider(client_id, client_secret)
        cluster = Cluster(
            cloud={'secure_connect_bundle': './secure-connect-socialmediadb2.zip'}, 
            auth_provider=auth_provider
        )
        session = cluster.connect(keyspace)

        # Example usage with results limit
        username = "realkrsna"
        results_limit = 5 # Set how many posts you want to fetch
        fetch_instagram_data(username, session, results_limit)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cluster' in locals():
            clustler.shutdown()

if __name__ == "__main__":
    main()