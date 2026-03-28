# SI 201 HW4 (Library Checkout System)
# Your name: Nahida Sultana, Mischa Rafferty, Tasnimah Uddin
# Your student id: 11038752, 7593 8200, 3176 9013
# Your email: nahidas@umich.edu, msraff@umich.edu, tasnimah@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.: 
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
  #When the code broke or failed, we asked GENAI on how to fix it
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#yes we did, but only to help guide us and help us with debugging and explanations, we still aligned with our goals by not asking it for exact answers
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

#from email.mime import text

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    listings = []
    seen_ids = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/rooms/" not in href:
            continue 

        match = re.search(r"/rooms/(\d+)", href)
        if not match:
            continue
            
        listing_id = match.group(1)
        if listing_id in seen_ids:
            continue

            # Use the a tag text itself for title
        text = a.get_text(" ", strip=True)

            # Sometimes text may be empty, fallback to parent
        if not text:
            parent = a.find_parent()
            if parent:
                text = parent.get_text(" ", strip=True)

            # Clean up extra descriptors after "in"
        if "·" in text:
            title = text.split("·")[0].strip()
        else:
            title = text.strip()
        if title:
            listings.append((title, listing_id))
            seen_ids.add(listing_id)
        
    return listings
    
    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    text = soup.get_text(" ", strip=True)

    # --- Policy Number ---
    policy_number = "Pending"
    if "Exempt" in text:
        policy_number = "Exempt"
    else:
        match = re.search(r"(20\d{2}-00\d{4,6}STR|STR-\d{7})", text)
        if match:
            policy_number = match.group(1)
        else:
            json_match = re.search(r'"title":"Policy number","subtitle":"(\d+)', text)
            if json_match:
                policy_number = json_match.group(1)

    # --- Host Type ---
    host_type = "Superhost" if "Superhost" in text else "regular"

    # --- Host Name ---
    host_name = "Unknown"
    host_match = re.search(r"Hosted by ([A-Za-z &]+)", text)
    if host_match:
        host_name = host_match.group(1).strip()
        if "Joined" in host_name:
            host_name = host_name.split("Joined")[0].strip()

    # --- Room Type ---
    subtitle = ""
    h1 = soup.find("h1")
    if h1:
        subtitle = h1.get_text()

    if "Private" in subtitle:
        room_type = "Private Room"
    elif "Shared" in subtitle:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    # --- Location Rating ---
    location_rating = 0.0
    rating_match = re.search(r"Location\s*([0-9]\.[0-9])", text)
    if rating_match:
        location_rating = float(rating_match.group(1))

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)
    database = []

    for title, listing_id in listings:
        details = get_listing_details(listing_id)[listing_id]

        database.append((
            title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"]
        ))
    return database
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "Listing Title", "Listing ID", "Policy Number",
            "Host Type", "Host Name", "Room Type", "Location Rating"
        ])

        for row in sorted_data:
            # Clean the listing title
            clean_title = row[0].split(" Charming")[0].strip()  # remove extra descriptors
            # Write row with cleaned title
            writer.writerow([clean_title] + list(row[1:]))
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}
    for row in data:
        room_type = row[5]
        rating = row[6]
        if rating == 0.0:
            continue
        if room_type not in totals:
            totals[room_type] = 0
            counts[room_type] = 0

        totals[room_type] += rating
        counts[room_type] += 1

    averages = {}
    for room_type in totals:
        averages[room_type] = round(totals[room_type] / counts[room_type], 1)
    return averages
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid = []
    pattern1 = r"20\d{2}-00\d{3,6}STR"
    pattern2 = r"STR-\d{7}$"

    for row in data:
        listing_id = row[1]
        policy = row[2]
        if policy in ["Pending", "Exempt"]:
            continue
        if not (re.fullmatch(pattern1, policy) or re.fullmatch(pattern2, policy)):
            invalid.append(listing_id)

        #if not re.search(r"(20\d{2}-\d{6}STR|STR-\d{7})", policy):
            #invalid.append(listing_id)

        if not (re.search(pattern1, policy) or re.search(pattern2, policy)):
            print(listing_id, policy)
            invalid.append(listing_id)

    return invalid
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        #print("TOTAL LISTINGS:", len(self.listings))
        #for l in self.listings:
            #print(l)

        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").

        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))
        pass    
    
    def test_get_listing_details(self):
        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]
        results = [get_listing_details(i) for i in html_list]

        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        self.assertEqual(
            self.detailed_data[-1],
        ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)
    )
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        
        out_path = os.path.join(self.base_dir, "test.csv")
        output_csv(self.detailed_data, out_path)

        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(
        rows[1],
        ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]
    )
        
        os.remove(out_path)


    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        result = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(result["Private Room"], 4.9)
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
 

def google_scholar_searcher(query) -> list: 
    query = query.replace(" ", "+")
    url = f"https://scholar.google.com/scholar?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"

    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []

    for item in soup.find_all("h3", class_="gs_rt"):
        title = item.get_text()
        if title:
            titles.append(title)
    return titles
