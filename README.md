At first, Thank you for visiting my Github, I would like to express my gratitude
This document documents my learning process as a data engineer. Below is a summary of my learning process and a file introduction:

1. Prototype folder: This is the nominatim file I created using OpenStreetMap (OSM) when I didn't understand the Google Places API. I originally wanted to capture the area of ​​a night market, but there was too little information and the scope of the night market was inaccurate.

2. Map: This is what I encountered when I started using the Google Places API. I began to understand the API's billing method and how to plan my program writing based on the free quota. I encountered many problems that I hadn't anticipated. 

The problems are as follows:
1. The data returned by the API was very dirty because it was created by netizens. I spent a lot of effort cleaning it up, including creating exception tables, how to handle 24-hour operation, a large number of errors and duplicates, and you can't view the night market types in Taipei as a whole of Taiwan, which would be extremely wrong.understanding that some night markets open in the morning (affecting the Uni Key and causing the inability to import SQL)
2. Business logic will affect the overall schema partitioning. You must understand multiple logics to successfully establish it, especially how primary keys and data should be linked and how to smoothly communicate with team members.
3. A painful lesson learned: always use logs and error filtering. Don't just print out errors directly. A large number of error messages won't solve any problems, and AI can't help you solve them either.
4. Initially, I thought I could use a small amount of data to test whether the database import was correct, but I later found that even if there was only one problem with a field or key-value pair in the database rules, the entire system would report an error, forcing me to revert to the data cleanup process for debugging.
