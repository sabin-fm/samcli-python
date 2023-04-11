from datetime import datetime
import sys
from typing import Any, List, Literal, Optional
from enum import Enum

from pydantic import BaseModel, Extra, validator


GOALS = Literal[
    "Stress around me",
    "Stress and mood navigation planner",
    "Family and friends",
    "Mental health trends",
    "Hormonal health tracker",
    "Order an epigenetic test"
    ]

HORMONAL_TRACKER = Literal[
    "Cycle Tracker",
    "Pregnancy and Beyond",
    "Hormone Therapy",
    "Sports and Fitness",
    "Men’s Hormonal Health",
    "Healthy aging"
]


class UserSchema(BaseModel):
    """Base Model For User"""
    id: str
    organizationId: str

    assessment_ids: List[str]
    
    firstName: str
    lastName: str
    gender: str
    age: int
    dob: str
    phone_number:str
    profile_image_url: str
    zip_code: str
    isDionysusAdmin: bool
    email: str
    email_verified: bool

    goals: List[GOALS]
    
    
    
    onBoarding: bool
    
    # page_index: int
    onboarding_page_tracker: int

    createdAt: str
    updatedAt: str

    hormonaltracker_flag: bool
    hormonal_tracker: List[HORMONAL_TRACKER]

    

    # Data sources fields
    fb_link_status: bool
    fb_token: str

    slack_link_status: bool
    slack_token: str
    
    twitter_link_status: bool
    twitter_handle: str
    twitter_secret: str
    twitter_token: str

    journal_text: List[str]