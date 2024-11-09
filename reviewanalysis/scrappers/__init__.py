import sys
import os
from .amazonscrapper import AmazonScrapper
from .flipkartscrapper import FlipKartScrapper
# Add the parent directory of `scrappers` to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
__all__=["AmazonScrapper","FlipKartScrapper"]