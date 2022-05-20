# Feature Flag Enables
# found here: https://superset.apache.org/docs/security/#public
PUBLIC_ROLE_LIKE_GAMMA = True
# found here: https://superset.apache.org/docs/installation/sql-templating/
ENABLE_TEMPLATE_PROCESSING = True

# reporting and alerts configuration
# found here:https://superset.apache.org/docs/installation/alerts-reports/#detailed-config
import logging
import os
from datetime import timedelta
from typing import Optional

from cachelib.file import FileSystemCache
from celery.schedules import crontab

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,


    "DASHBOARD_CACHE": True,
    # Experimental feature introducing a client (browser) cache
    "CLIENT_CACHE": True,
}

JINJA_CONTEXT_ADDONS = {
    'my_crazy_macro': lambda x: x*2,
}

def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)

DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

class CeleryConfig:
    broker_url = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    imports = ('superset.sql_lab', "superset.tasks", "superset.tasks.thumbnails", )
    result_backend = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 600,
            'soft_time_limit': 600,
            'ignore_result': True,
        },
    }
    beat_schedule = {
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': crontab(minute='*', hour='*'),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': crontab(minute=0, hour=0),
        },
    }
CELERY_CONFIG = CeleryConfig

CELERYBEAT_SCHEDULE = {
    'cache-warmup-hourly': {
        'task': 'cache-warmup',
        'schedule': crontab(minute=0, hour='*'),  # hourly
        'kwargs': {
            'strategy_name': 'top_n_dashboards',
            'top_n': 10,
            'since': '7 days ago',
        },
    },
}


REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

CACHE_DEFAULT_TIMEOUT = 300

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "DEBUG": True,
    "CACHE_KEY_PREFIX": "data_cache_results",  # make sure this string is unique to avoid collisions
    "CACHE_DEFAULT_TIMEOUT": 300, 
    #CACHE_OPTIONS #Entries in CACHE_OPTIONS are passed to the redis client as **kwargs
    "CACHE_REDIS_HOST": get_env_variable("REDIS_HOST"),
    "CACHE_REDIS_PORT": get_env_variable("REDIS_PORT"),
    "CACHE_REDIS_PASSWORD": get_env_variable("REDIS_ACCESS_KEY")
    #CACHE_REDIS_DB
    #CACHE_REDIS_URL
}

SQLLAB_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6

SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Slack configuration
SLACK_API_TOKEN = "xoxb-"

# Email configuration
# setup using sendgrid account
SMTP_HOST = "smtp.sendgrid.net" #change to your host
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "apikey"
SMTP_PORT = 587 # your port eg. 587
SMTP_PASSWORD = "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"
SMTP_MAIL_FROM = "richard.blanchette@apexcleanenergy.com"

# WebDriver configuration
# If you use Firefox, you can stick with default values
# If you use Chrome, then add the following WEBDRIVER_TYPE and WEBDRIVER_OPTION_ARGS
# WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
]

# This is for internal use, you can keep http
WEBDRIVER_BASEURL="http://superset:8088"

# This is the link sent to the recipient, change to your domain eg. https://superset.mydomain.com
WEBDRIVER_BASEURL_USER_FRIENDLY="http://superset.adh.apexcleanenergy.com"