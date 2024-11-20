# Checker

A Python-based checking system designed to analyze and report on HTML issues that can impact SEO and accessibility.

## Overview

This tool is particularly useful for SEO professionals and web developers who want to ensure their web pages are optimized for search engines and accessible to all users. It checks for common HTML issues that can affect page ranking and user experience.

## Features

- **Link Validation**: Checks if all links on a page are accessible and reports broken links.
- **HTML Structure Analysis**: Identifies issues with HTML tags, such as empty tags, missing alt attributes on images, and duplicate IDs.
- **Heading Hierarchy Check**: Ensures proper use of heading tags for better SEO and accessibility.
- **Deprecated Tags Detection**: Finds and reports deprecated HTML tags that should be replaced with modern alternatives.
- **Form Validation**: Checks for missing form attributes like `action` and associated labels for inputs.
- **Meta Tag Verification**: Ensures essential meta tags like `viewport` and `description` are present.
- **Character Encoding Check**: Verifies that character encoding is declared in the HTML.
- **Inline Style and JavaScript Detection**: Reports inline styles and JavaScript attributes that can affect maintainability.
- **List and Table Structure Validation**: Ensures lists and tables are properly structured.

## Installation

First, install `uv` package manager:

### macOS

```bash
brew install uv
```

### Linux

```bash
curl -fsSL https://get.uv.cli.rs | sh
```

## Running the Application

Navigate to the project directory and run:

```bash
cd checker
uv run app.py
```

The script will read URLs from a `urls.txt` file located in the same directory and generate a CSV report of any issues found.

## Benefits for SEO Professionals

- **Improved Search Engine Ranking**: By identifying and fixing HTML issues, you can improve the search engine ranking of your web pages.
- **Enhanced User Experience**: Ensures that web pages are accessible and user-friendly, which can lead to higher engagement and conversion rates.
- **Efficient Auditing**: Automates the process of checking multiple web pages, saving time and effort in manual audits.

## License

MIT License
