# pylint: disable=R0913

'''
Models for the Resume API. Each class is related to
'''

from dataclasses import dataclass


@dataclass
class Experience:
    '''
    Experience Class
    '''
    title: str
    company: str
    start_date: str
    end_date: str
    description: str
    logo: str
    id: int = None


@dataclass
class Education:
    '''
    Education Class
    '''
    course: str
    school: str
    start_date: str
    end_date: str
    grade: str
    logo: str
    id: int = None


@dataclass
class Skill:
    '''
    Skill Class
    '''
    name: str
    proficiency: str
    logo: str


@dataclass
class UserInformation:
    '''
    UserInformation Class
    '''
    name: str
    email_address: str
    phone_number: str
