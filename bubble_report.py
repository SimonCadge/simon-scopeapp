from pydantic import BaseModel
from pydantic.functional_validators import BeforeValidator, AfterValidator
from dataclasses import dataclass
import csv
from csv import DictReader
from datetime import datetime
from typing import List, Tuple
from typing_extensions import Annotated
import jinja2
import pdfkit
import statistics as pystatistics
import os
import sys, getopt
import shutil

class User(BaseModel):
    """Class to define a single user"""
    id: int
    ig_username: str
    ig_num_followers: int

def coerce_str_to_list(str_rep: str) -> List[str]:
    if str_rep == "[]" or str_rep == 'NULL':
        return []
    else:
        str_rep = str_rep[2:-2]
        captions = str_rep.split('","')
        return captions

class Post(BaseModel):
    """Class to define a single post"""
    person_id: int
    taken_at: datetime
    caption_text: str
    caption_tags: Annotated[List[str], BeforeValidator(coerce_str_to_list)]
    like_count: int
    comment_count: int

    #TODO: Something is missing here. My counts of 'Influencers with activity' and 'Posts' differ from that in the example
    def is_relevant_to_bubbleroom(self) -> bool:
        return "@bubbleroom" in self.caption_text \
            or "bubbleroom" in self.caption_tags \
            or "bubbleroomstyle" in self.caption_tags
    
    def get_engagement(self, user: User) -> float:
        engagement = (self.like_count + self.comment_count) / user.ig_num_followers
        return engagement * 100.0 #as percentage

    def has_bubbleroom_hashtag(self) -> bool:
        return "bubbleroom" in self.caption_tags
    
    def has_bubbleroomstyle_hashtag(self) -> bool:
        return "bubbleroomstyle" in self.caption_tags
    
    def has_mention(self) -> bool:
        return "@bubbleroom" in self.caption_text

class Statistics(BaseModel):
    """Class to keep track of overall statistics"""
    start_date: str
    end_date: str
    num_influencers: int
    num_active_influencers: int
    num_posts: int
    num_post_mentions: int
    num_bubbleroom_hashtags: int
    num_bubbleroomstyle_hashtags: int
    num_photo_tags: int
    actual_reach: int
    overall_engagement: float
    num_likes: int
    num_comments: int

class UserStatistics(BaseModel):
    """Class to keep track of the statistics for a single influencer"""
    user: User
    general_engagement: float
    specific_engagement: float
    num_comments: int
    num_likes: int
    num_posts: int
    num_post_mentions: int
    num_bubbleroom_hashtags: int
    num_bubbleroomstyle_hashtags: int
    num_photo_tags: int
    score: int        

UsersById = dict[int, User]

def parse_users(file_path: str) -> UsersById:
    users: UsersById = {}
    with open(file_path) as file_to_parse:
        reader = DictReader(file_to_parse)
        for row in reader:
            user = User(**row)
            users[user.id] = user
    return users

PostsById = dict[int, List[Post]]

def parse_posts(file_path: str, start_date: datetime, end_date: datetime) -> PostsById:
    posts_by_user: PostsById = {}
    with open(file_path) as file_to_parse:
        reader = DictReader(file_to_parse)
        for row in reader:
            post = Post(**row)
            if post.taken_at >= start_date and post.taken_at <= end_date:
                if post.person_id in posts_by_user:
                    posts = posts_by_user[post.person_id]
                    posts.append(post)
                else:
                    posts_by_user[post.person_id] = [post]
    return posts_by_user

def process_posts_for_user(user: User, posts: List[Post]) -> UserStatistics:
    engagements = []
    specific_engagements = []
    num_comments = 0
    num_likes = 0
    num_posts = 0
    num_post_mentions = 0
    num_bubbleroom_hashtags = 0
    num_bubbleroomstyle_hashtags = 0
    num_photo_tags = 0
    for post in posts:
        post_engagement = post.get_engagement(user)
        engagements.append(post_engagement)
        if post.is_relevant_to_bubbleroom():
            specific_engagements.append(post_engagement)
            num_comments += post.comment_count
            num_likes += post.like_count
            num_posts += 1
            if post.has_mention():
                num_post_mentions += 1
            if post.has_bubbleroom_hashtag():
                num_bubbleroom_hashtags += 1
            if post.has_bubbleroomstyle_hashtag():
                num_bubbleroomstyle_hashtags += 1
            num_photo_tags += 0 # TODO: What are photo tags? https://developers.facebook.com/docs/graph-api/reference/v17.0/photo/tags
    general_engagement = 0.0
    if len(engagements) > 0:
        general_engagement = pystatistics.mean(engagements)
    specific_engagement = 0.0
    if len(specific_engagements) > 0:
        specific_engagement = pystatistics.mean(specific_engagements)
    score = num_posts + num_post_mentions + num_bubbleroom_hashtags + num_bubbleroomstyle_hashtags + num_photo_tags
    user_statistics = UserStatistics(user=user, general_engagement=general_engagement, specific_engagement=specific_engagement,\
        num_comments=num_comments, num_likes=num_likes, num_posts=num_posts, num_post_mentions=num_post_mentions,\
        num_bubbleroom_hashtags=num_bubbleroom_hashtags, num_bubbleroomstyle_hashtags=num_bubbleroomstyle_hashtags, num_photo_tags=num_photo_tags, score=score)
    return user_statistics

def process_overall_statistics(user_statistics: List[UserStatistics], start_date: datetime, end_date: datetime) -> Statistics:
    start_date = start_date.strftime("%d %B %Y")
    end_date = end_date.strftime("%d %B %Y")
    num_influencers = len(user_statistics)
    num_active_influencers = 0
    num_posts = 0
    num_post_mentions = 0
    num_bubbleroom_hashtags = 0
    num_bubbleroomstyle_hashtags = 0
    num_photo_tags = 0
    actual_reach = 0
    engagements = []
    num_likes = 0
    num_comments = 0
    for user in user_statistics:
        if user.score > 0:
            num_active_influencers += 1
        num_posts += user.num_posts
        num_post_mentions += user.num_post_mentions
        num_bubbleroom_hashtags += user.num_bubbleroom_hashtags
        num_bubbleroomstyle_hashtags += user.num_bubbleroomstyle_hashtags
        num_photo_tags += user.num_photo_tags
        actual_reach += (user.num_comments + user.num_likes) # TODO: What is actual reach
        engagements.append(user.specific_engagement)
        num_likes += user.num_likes
        num_comments += user.num_comments
    overall_engagement = pystatistics.mean(engagements)
    statistics = Statistics(start_date=start_date, end_date=end_date, num_influencers=num_influencers, num_active_influencers=num_active_influencers, num_posts=num_posts,\
        num_post_mentions=num_post_mentions, num_bubbleroom_hashtags=num_bubbleroom_hashtags, num_bubbleroomstyle_hashtags=num_bubbleroomstyle_hashtags,\
        num_photo_tags=num_photo_tags, actual_reach=actual_reach, overall_engagement=overall_engagement, num_likes=num_likes, num_comments=num_comments)
    return statistics

def generate_html_string(statistics: Statistics, user_statistics: List[UserStatistics], search_path: str) -> str:
    template_loader = jinja2.FileSystemLoader(searchpath=search_path)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "base.html"
    template = template_env.get_template(TEMPLATE_FILE)

    return template.render(statistics=statistics, user_statistics=user_statistics, search_path=search_path)

def generate_html(statistics: Statistics, user_statistics: List[UserStatistics]) -> str:
    html_string = generate_html_string(statistics, user_statistics, "static/")

    try:
        shutil.rmtree('html-output')
    except FileNotFoundError:
        pass

    shutil.copytree('static', 'html-output/static')

    with open("html-output/out.html", "w") as f:
        f.write(html_string)

def generate_pdf(statistics: Statistics, user_statistics: List[UserStatistics]):
    search_path = os.path.abspath('static/')
    html_string = generate_html_string(statistics, user_statistics, search_path)

    options = {
        "enable-local-file-access": "",
        "allow": search_path,
        "orientation": "Landscape",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0"
    }

    try:
        shutil.rmtree('pdf-output')
    except FileNotFoundError:
        pass

    os.makedirs('pdf-output')
    pdfkit.from_string(html_string, 'pdf-output/out.pdf', options=options)

def main(argv):
    help_requested = False
    create_pdf = False
    create_html = True
    start_date = datetime(2021, 1, 1, 0, 0, 0)
    end_date = datetime(2021, 1, 31, 23, 59, 59)
    user_csv = "users.csv"
    user_posts_csv = "user_posts.csv"
    opts, args = getopt.getopt(argv, "hs:e:u:p:", ["help", "create_pdf=", "create_html=", "start_date=", "end_date=", "user_csv=", "user_posts_csv="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('''
Basic Usage\n
`python bubble_report.py [flags]` - general call signature\n
`python bubble_report.py --create_pdf=True` - e.g. enable pdf generation\n
`python bubble_report.py -s "2021-02-01T12:00:00" -e "2021-04-01T12:00:00"` - e.g. custom start and end dates\n
Command Line Options\n
\tOption\t\tFlag\t\t\t\t\t\t\tDescription\t\t\t\t\t\t\t\t\tDefault\n
\t---\t\t---\t\t\t\t\t\t\t---\t\t\t\t\t\t\t\t\t\t---\n
\thelp\t\t`-h` or `--help`\t\t\t\t\tdisplay command line documentation\n
\tcreate_pdf\t`--create_pdf=True` or `--create_pdf=False`\t\tgenerate a pdf output file\t\t\t\t\t\t\t`False`\n
\tcreate_html\t`--create_html=True` or `--create_html=False`\t\tgenerate an html output file\t\t\t\t\t\t\t`True`\n
\tstart_date\t`-s "date"` or `--start_date="date"`\t\t\tset start date, accepts strings in ISO 8601 format\t\t\t\t`2021-01-01T00:00:00`\n
\tend_date\t`-e "date` or `--end_date="date"`\t\t\tset end date, accepts strings in ISO 8601 format\t\t\t\t`2021-01-31T23:59:59`\n
\tuser_csv\t`-u "file_path"` or `--user_csv="file_path"`\t\tset file path for user csv, path is relative to current working directory\t`users.csv`\n
\tuser_posts_csv\t`-p "file_path` or `--user_posts_csv="file_path"`\tset file path for user posts csv, path is relative to current working directory\t`user_posts.csv`
            ''')
            sys.exit()
        elif opt == "--create_pdf":
            create_pdf = arg
        elif opt == "--create_html":
            create_html = arg
        elif opt in ("-s", "--start_date"):
            start_date = datetime.fromisoformat(arg)
        elif opt in ("-e", "--end_date"):
            end_date = datetime.fromisoformat(arg)
        elif opt in ("-u", "--user_csv"):
            user_csv = arg
        elif opt in ("-p", "--user_posts_csv"):
            user_posts_csv = arg

    if end_date < start_date:
        print("Start date must be before End date")
        sys.exit()

    users: UsersById = parse_users(user_csv)
    posts_by_user: PostsById = parse_posts(user_posts_csv, start_date, end_date)

    user_statistics = []
    for user_id, user_posts in posts_by_user.items():
        user_statistics.append(process_posts_for_user(users[user_id], user_posts))

    statistics = process_overall_statistics(user_statistics, start_date, end_date) 

    if create_html:
        generate_html(statistics, user_statistics)

    if create_pdf:
        generate_pdf(statistics, user_statistics)

if __name__ == "__main__":
    main(sys.argv[1:])
