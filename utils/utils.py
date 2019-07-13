"""Utility module"""
import os


def get_root():
    """Returns root location of project"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
