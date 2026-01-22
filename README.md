
---

## EA Email Finder

**EA Email Finder** is a Windows desktop application designed to **check email availability and service association** using publicly accessible validation endpoints.

The tool determines whether an email address:

* Is already **linked to an Electronic Arts (EA) account**
* Is **available or unavailable on Microsoft services**
* Or cannot be reliably validated

The project focuses on **accuracy, clarity, session recovery, and long-running batch scans**, all through a clean and responsive graphical interface.

---

## Table of Contents

* [Features](#features)
* [How It Works](#how-it-works)
* [Getting Started](#getting-started)
* [Usage](#usage)

  * [Check a Single Email](#check-a-single-email)
  * [Check Multiple Emails (Bulk Scan)](#check-multiple-emails-bulk-scan)
  * [Resume Interrupted Scans](#resume-interrupted-scans)
* [Result Classification](#result-classification)
* [Output Formats](#output-formats)
* [Releases](#releases)
* [License](#license)

---

## Features

* **Single Email Check**
  Instantly verify the status of a single email address.

* **Bulk Email Scanning**
  Load a `.txt` file containing email addresses and scan them sequentially.

* **Dual-Service Validation**

  * EA email existence check
  * Microsoft availability check

* **Live Progress Tracking**

  * Current email being checked
  * Total processed count in real time

* **Resume Support**
  Automatically resumes unfinished scans after interruption or closure.

* **Multiple Export Formats**
  Save available emails as **JSON** or **TXT**.

* **Long-Run Safe**
  Designed for overnight or extended scans with controlled delays and retry logic.

---

## How It Works

For each email address, the application performs the following steps:

1. **EA Validation**

   * Sends a request to EA’s public email validation endpoint.
   * Determines whether the email is already registered with EA.

2. **Microsoft Validation (Conditional)**

   * If the email is linked to EA, the app checks its availability on Microsoft services.
   * Uses Microsoft’s public signup availability endpoint.

3. **Classification**

   * Results are interpreted and categorized based on real response fields and heuristics.

No login, authentication, brute force, or security bypass techniques are used.

---

## Getting Started

For best performance, use the **precompiled Windows executable**.

Download the latest version from the official releases page:

**Releases:**
[Releases](https://github.com/lI-Isekai-Il/EA-Email-Finder/releases)

Steps:

1. Download the executable
2. Run the application

---

## Usage

### Check a Single Email

1. Launch the application.
2. Enter an email address.
3. Click **CHECK** or press **Enter**.
4. The result appears instantly:

* **AVAILABLE** – Email is usable and available.
* **TAKEN** – Email is already in use or unavailable.
* **UNAVAILABLE** – Email could not be validated or is invalid.

---

### Check Multiple Emails (Bulk Scan)

1. Prepare a `.txt` file.

   * One email per line.
2. Click **Select File**.
3. Choose the input file.
4. Select output format:

   * **JSON** or **TXT**
5. Choose save location.
6. The scan begins automatically.

During the scan, the interface shows:

* Number of processed emails
* Currently checked email
* Live status updates

---

### Resume Interrupted Scans

If the application closes or is interrupted during a bulk scan:

* The next launch will detect the unfinished session.
* You will be asked whether to resume.
* Choose **YES**, then press **CHECK** to continue from the last saved index.

This is ideal for very large lists or overnight scans.

---

## Result Classification

Emails are internally categorized into folders:

* **AVAILABLE**

  * Linked to EA
  * Available on Microsoft

* **TAKEN**

  * Linked to EA
  * Not available on Microsoft

* **UNAVAILABLE**

  * Not linked to EA
  * Invalid format
  * Or validation error

---

## Output Formats

### JSON

Each available email is saved with metadata:

```json
{
  "email": "example@email.com",
  "date": "UTC timestamp",
}
```

Recommended for automation and future processing.

---

### TXT

* Plain text list of available emails

Best for manual use and quick review.

---

## Releases

All official builds are published here:

[Releases](https://github.com/lI-Isekai-Il/EA-Email-Finder/releases)

### Current Edition

* **EA Email Finder v1.00**

  * Stable
  * Balanced performance
  * Recommended for most users

Future optimized versions may be released separately.

---

## License

This project is released under a **custom author license**.

* Personal, educational, and research use only
* No commercial use
* No redistribution or rebranding
* No affiliation with EA, or Microsoft

Full license text is included inside the application and source code.

---

## Author & Ownership

**Author & Owner:**
The Immortal Emperor – The Manipulator of Humans
The One and The Only Vampire
The Emperor of Kings
lI_Isekai_Il | lI-Isekai-Il

**Official Repository:**
[EA Email Finder](https://github.com/lI-Isekai-Il/EA-Email-Finder)

---

**Respect the code.
Respect the author.
Respect the license.**

---
