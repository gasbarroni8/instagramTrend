import os
import argparse
import platform
from models import (
	Instagram
)

basePath = os.path.dirname(os.path.abspath(__file__))

config = {
	'USERNAME':'',
	'PASSWORD':'',
	'DB_HOST':'',
	'DB_PORT':,
	'DB_DATABASE':'',
	'DB_USERNAME':'',
	'DB_PASSWORD':'',
	'DRIVER_PATH': basePath + '/drivers/'+ platform.system() +'/chromedriver'
}

parser = argparse.ArgumentParser()
parser.add_argument("-t", help="crawl type")
args = parser.parse_args()

instagram = Instagram(config)

if args.t == "follow":
	instagram.followUser()
elif args.t == "hashtag":
	instagram.getHashTag()
elif args.t == "unfollow":
	instagram.unfollowUser()
elif args.t == "followlist":
	instagram.getFollowList()