from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive

import os

from time import sleep

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        get_preview()
        submit_order()
        store_receipt_as_pdf(order['Order number'])
        order_another_robot()
    archive_receipts()

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order/")

def get_orders():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables()
    orders = table.read_table_from_csv(
            "orders.csv"
    )
    return orders

def close_annoying_modal():
    """Closes the annoying popup at the start"""
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):
    """Fills in the order form"""
    page = browser.page()
    page.select_option("#head", order['Head'])
    body_id = "#id-body-" + order['Body']
    page.click(body_id)
    page.fill("//input[@class='form-control' and @type='number']", order['Legs'])
    page.fill("#address", order['Address'])

def get_preview():
    """Opens the preview for the robot"""
    page = browser.page()
    page.click("#preview")

def submit_order():
    """Submits the robot order"""
    page = browser.page()
    success = False
    while not success:
        page.click("#order")
        try:
            page.wait_for_selector("//div[@class='alert alert-danger']", timeout=500,)
        except:
            success = True

def store_receipt_as_pdf(order_number):
    """Stores the receipt as a PDF"""
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    filename = "output/receipts/receipt" + order_number + ".pdf"
    pdf.html_to_pdf(sales_results_html, filename)
    screenshot = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screenshot, filename)
    os.remove(screenshot)

def screenshot_robot(order_number):
    """Stores a screenshot of the robot"""
    page = browser.page()
    filename = "output/screenshot" + order_number + ".png"
    page.screenshot(path=filename)
    return filename

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Adds the screenshot to the receipt"""
    pdf = PDF()    
    pdf.add_files_to_pdf([pdf_file, screenshot], pdf_file)

def order_another_robot():
    """Clicks the Order another robot button"""
    page = browser.page()
    page.click("#order-another")

def archive_receipts():
    """Zips all the receipts"""
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "output/receipts.zip")
