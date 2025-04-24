import praw
import os
from datetime import datetime


def format_replies(comment, depth=0):
    content = '  ' * depth + f"→ ✨{comment.score}✨ {comment.body}\n"
    for reply in comment.replies:
        content += format_replies(reply, depth + 1)
    return content


def format_post(reddit, post):
    submission = reddit.submission(url=f"https://reddit.com{post.permalink}")
    content = f"""标题: {submission.title}
作者: u/{post.author.name}
发布时间: {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')}
正文: {submission.selftext}
点赞数: {submission.score}
评论总数: {submission.num_comments}
"""
    submission.comments.replace_more(limit=2)

    # 遍历所有评论（包含子评论）
    for comment in submission.comments.list():
        content += f"""{format_replies(comment)}\n""" + "=" * 3 + "\n"
    return content


class Reddit:
    def __init__(self):
        self.client = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            username=os.environ.get("REDDIT_USERNAME"),
            password=os.environ.get("REDDIT_PASSWORD"),
            user_agent="testscript by u/kangtian1024",
        )

        if not self.client.user.me():
            raise Exception("Login reddit error")

    def get_last_posts(self, subreddit, limit=10):
        # subreddit like "wallstreetbets"
        subreddit = self.client.subreddit(subreddit)
        posts = subreddit.new(limit=limit)
        return list(map(lambda x: format_post(self.client, x), posts))


if __name__ == "__main__":
    reddit = Reddit()
    reddit.get_last_posts("wallstreetbets")
