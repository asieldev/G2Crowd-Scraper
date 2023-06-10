import asyncio
from dataclasses import asdict, dataclass, field

import pandas as pd
from playwright.async_api import Error, async_playwright


# `@dataclass` is a decorator in Python that allows you to create classes with attributes and methods
# without having to write boilerplate code. In this case, the `GProduct` class is defined with five
# attributes: `title`, `reviews`, `seo_ease_use_average`, `seo_quality_support_average`, and
# `seo_ease_setup_average`. Each attribute has a default value of `None` or `0.0`. This class is used
# to create instances of products that will be scraped from a website using Playwright. The scraped
# data will be stored in instances of this class and then added to a list of products.
@dataclass
class GProduct:
    title: str = None
    reviews: int = None
    seo_ease_use_average: float = 0.0
    seo_quality_support_average: float = 0.0
    seo_ease_setup_average: float = 0.0


# The `@dataclass` decorator is used to define a class with attributes and methods. In this case, the
# `GProductList` class is defined with a single attribute `product_list` which is a list of `GProduct`
# objects. The `dataframe()` method returns a pandas DataFrame object that is created from the
# `product_list` attribute using the `json_normalize()` function. The `save_to_csv()` and
# `save_to_json()` methods save the `product_list` attribute to a CSV and JSON file, respectively,
# using the `to_csv()` and `to_json()` methods of the pandas DataFrame object returned by the
# `dataframe()` method.
@dataclass
class GProductList:
    product_list: list[GProduct] = field(default_factory=list)

    def dataframe(self):
        """The function returns a pandas dataframe by normalizing a list of product objects into a JSON format.

        Returns
        -------
            The function `dataframe` is returning a pandas DataFrame object that is created by normalizing a
        list of product objects into a JSON format using the `json_normalize` function from the pandas
        library. The `asdict` function is used to convert each product object into a dictionary before
        passing it to `json_normalize`. The `sep` parameter is used to specify the separator character to
        use when flattening

        """
        return pd.json_normalize(
            (asdict(product) for product in self.product_list),
            sep="_",
        )

    def save_to_csv(self, filename):
        """This function saves a pandas dataframe to a CSV file with the specified filename.

        Parameters
        ----------
        filename
            The name of the file to which the data will be saved as a CSV file. The ".csv" extension will be
        added automatically to the filename.

        """
        self.dataframe().to_csv(f"{filename}.csv", index=False)

    # Save the result as JSON
    def save_to_json(self, filename):
        """This function saves a pandas dataframe to a JSON file with a specified filename.

        Parameters
        ----------
        filename
            The filename parameter is a string that represents the name of the file where the JSON data will be
        saved. It should not include the file extension as it will be added automatically in the function.

        """
        self.dataframe().to_json(f"{filename}.json", orient="records")


async def scrape_g2crowd_urls(g2crowd_urls):
    """This function scrapes data from a list of URLs using Playwright, creates instances of a class with
    the scraped data, and saves the data to CSV and JSON files.

    Parameters
    ----------
    g2crowd_urls
        `g2crowd_urls` is a list of URLs that will be scraped for data using Playwright. The loop in the
    code block will iterate through each URL in the list and scrape specific data points from each page.

    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()

        products_list = GProductList()

        # This code block is iterating through a list of URLs (`g2crowd_urls`) and scraping data from each URL
        # using Playwright. The scraped data is then used to create instances of the `GProduct` class, which
        # are added to a `GProductList` object. The `GProductList` object is then used to save the scraped
        # data to a CSV and JSON file. The specific data being scraped includes the product title, number of
        # reviews, and three SEO-related metrics (`seo_ease_use_average`, `seo_quality_support_average`, and
        # `seo_ease_setup_average`). The XPaths for each of these data points are defined within the loop.
        for url in g2crowd_urls:
            try:
                await page.goto(url)
                await page.wait_for_load_state()

                # These are XPath expressions that are used to locate specific elements on a web page. Each expression
                # is assigned to a variable (`title_xpath`, `reviews_xpath`, `seo_ease_use_average_xpath`,
                # `seo_quality_support_average_xpath`, and `seo_ease_setup_average_xpath`) and is used later in the
                # code to locate the corresponding element on the page using Playwright's `page.locator()` method. The
                # elements being located are the product title, number of reviews, and three SEO-related metrics
                # (`seo_ease_use_average`, `seo_quality_support_average`, and `seo_ease_setup_average`).
                title_xpath = '//a[@class="c-midnight-100"]'
                reviews_xpath = '//a[@class="link js-log-click" and @href="https://www.g2.com/products/conductor/reviews#reviews" and \
                @href="https://www.g2.com/products/conductor/reviews#reviews"]'
                seo_ease_use_average_xpath = '//div[@class="center-center fw-semibold text-medium" and @style="color: #ff492c"]'
                seo_quality_support_average_xpath = '//div[@class="center-center fw-semibold text-medium" and @style="color: #5a39a2"]'
                seo_ease_setup_average_xpath = '//div[@class="center-center fw-semibold text-medium" and @style="color: #5a39a2"]'

                product = GProduct()

                product.title = str(
                    await page.locator(title_xpath).inner_text()
                )
                product.reviews = int(
                    str(await page.locator(reviews_xpath).all_inner_texts())
                    .split(" ")[1]
                    .split("'")[1]
                )
                product.seo_ease_use_average = float(
                    str(
                        await page.locator(
                            seo_ease_use_average_xpath
                        ).inner_text()
                    )
                )
                product.seo_quality_support_average = float(
                    str(
                        await page.locator(
                            seo_quality_support_average_xpath
                        ).inner_text()
                    )
                )
                product.seo_ease_setup_average = float(
                    str(
                        await page.locator(
                            seo_ease_setup_average_xpath
                        ).inner_text()
                    )
                )

            except Error as e:
                print(f"Error scraping {url}: {str(e)}")

            products_list.product_list.append(product)

        # `products_list.save_to_csv('google_maps_data')` and `products_list.save_to_json('google_maps_data')`
        # are saving the scraped data to CSV and JSON files, respectively. The `save_to_csv()` method of the
        # `GProductList` class saves the data to a CSV file with the specified filename
        # (`google_maps_data.csv` in this case), while the `save_to_json()` method saves the data to a JSON
        # file with the same filename (`google_maps_data.json`). The data is saved in the format of a pandas
        # DataFrame object that is created from the `product_list` attribute of the `GProductList` object
        # using the `dataframe()` method.
        products_list.save_to_csv("g2_data")
        products_list.save_to_json("g2_data")

        await browser.close()


# `g2crowd_urls` is a list that contains a single URL string
# `"https://www.g2.com/products/conductor/features"`. This URL is the page that will be scraped by the
# `scrape_g2crowd_urls` function.
g2crowd_urls = ["https://www.g2.com/products/conductor/features"]

# `if __name__== "__main__":` is a conditional statement that checks if the current script is being
# run as the main program. If it is, then it executes the code inside the block, which in this case is
# calling the `scrape_g2crowd_urls` function with the `g2crowd_urls` list as an argument using
# `asyncio.run()`. This allows the script to be run as a standalone program, but not when it is
# imported as a module in another script.
if __name__ == "__main__":
    asyncio.run(scrape_g2crowd_urls(g2crowd_urls))
