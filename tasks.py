from robocorp.tasks import task
from robocorp import browser, http
from RPA.PDF import PDF
from RPA.Archive import Archive
import pandas as pd
import time
import os
import tempfile


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_webtisite()
    numberOfOrders, orders = get_orders()
    # for loop the size of the number of orders
    for orderNumber in numberOfOrders:
        close_annoying_modal()
        fill_the_form(*next(orders))
        preview_robot()
        # time.sleep(5)
        order_robot()
        #time.sleep(5)
        pdf_file = store_receipt_as_pdf(orderNumber)
        screenshot = take_screenshot(orderNumber)
        embed_screenshot_to_pdf(screenshot, pdf_file)
        click_order_another_robot()
    archive_reciepts()


def open_robot_order_webtisite():
    """Opens the RobotSpareBin Industries Inc. web site."""
    #browser.configure(slowmo=100)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Gets the orders from the RobotSpareBin Industries Inc. web site. and returns an iterator of orders."""
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    df = pd.read_csv("orders.csv")  # read the csv file
    df.set_index("Order number", inplace=True)
    os.remove("orders.csv")
    orderNumbers = df.index.tolist()
    order_iterator = get_order_iterator(df)
    return orderNumbers, order_iterator

def get_order_iterator(df):
    """Gets the orders from the RobotSpareBin Industries Inc. web site. and returns an iterator of orders."""
    for _, row in df.iterrows():
        yield row["Head"], row["Body"], row["Legs"], row["Address"]

def close_annoying_modal():
    """Closes the annoying modal that pops up when you open the web site."""
    page = browser.page()
    page.click("css=#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")

def fill_the_form(head, body, legs, address):
    """Fills the order form."""
    page = browser.page()
    page.select_option("css=#head", str(head))
    page.click(f"css=#id-body-{body}")
    page.fill("xpath=(//div[@class='form-group'])[3]//input[@class='form-control']", str(legs))
    page.fill("css=#address", str(address))

def preview_robot():
    """Previews the robot."""
    page = browser.page()
    page.click("css=#preview")

def order_robot():
    """Orders the robot."""
    page = browser.page()
    
    while True:  # Keep checking until successful
        page.click("css=#order")
        next_order_button = page.query_selector("css=#order-another")
        if next_order_button:
            print("Order successful")
            break  # Exit the while loop
        else:
            print("Order failed, trying again")

def store_receipt_as_pdf(order_number):
    """Saves the receipt."""
    print(f"Storing receipt as PDF for order number: {order_number}")
    page = browser.page()
    receipt_html = page.locator("css=#receipt").inner_html()
    pdf = PDF()
    path = f"receipt/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, path)
    return path

def take_screenshot(order_number):
    """Takes a screenshot of the robot."""
    page = browser.page()
    path = f"pictures/robot-{order_number}.png"
    page.screenshot(path= path)
    return path

def embed_screenshot_to_pdf(screenshot, pdf_file):
    """Embeds the screenshot to the receipt PDF."""
    pdf = PDF()
    pdf.add_files_to_pdf(files = [pdf_file, screenshot], target_document= pdf_file)

def click_order_another_robot():
    """Clicks the order another robot button."""
    page = browser.page()
    page.click("css=#order-another")

def archive_reciepts():
    """Creates ZIP archive of the receipts and the images."""
    lib = Archive()
    lib.archive_folder_with_zip("receipt", "output/receipts.zip")
