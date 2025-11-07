Smart Travel Project
Project Overview

The Smart Travel Project is a Python-based tool that validates and normalizes user input data for a travel planning application. It ensures that user profiles and travel queries conform to a defined schema and converts free-form inputs into standardized formats. By enforcing schema rules and normalizing preferences (e.g. travel interests) and budgets, this project provides a clean, consistent foundation for building personalized travel itinerary recommendations or other travel-related analytics. This README provides an overview of the project structure, features, usage, and guidance on extending the codebase.

Features

Schema Validation: Uses the JSON Schema standard (Draft 7) via the jsonschema library to validate the structure of user_profile and user_query data. The validation checks for required fields, data types, and allowed values. All validation errors are collected and reported together using Draft7Validator.iter_errors (so the user can see all issues at once rather than failing on the first error).

Taxonomy Normalization: Implements a mapping of free-text user preferences to a fixed internal taxonomy. For example, a user preference like "chill" is normalized to the category "relax", and "culinary" is normalized to "foodie". This ensures that different words with the same meaning are treated uniformly (improving consistency in downstream processing like recommendation engines).

Budget Normalization: Supports user budgets in different currencies and normalizes them using stubbed exchange rates. For instance, if a query’s budget is given in EUR or JPY, the system will convert it to a base currency (e.g. USD) or a consistent internal representation using predefined conversion rates (for example, converting 1000 EUR to 1200 USD if using a 1.2 rate). This allows the application to compare and compute budgets without worrying about currency differences.

DTOs (Data Transfer Objects): Defines Python dataclasses to represent the normalized user profile and query. After validation and normalization, the data is loaded into these structured objects (e.g. UserProfile, UserQuery classes), making it easy to access user attributes in code with proper types. This provides clarity and type safety when the normalized data is used elsewhere in the application.

Fixtures for Testing: Includes a set of sample user profiles and queries (fixtures) for testing purposes. These fixtures cover both valid examples (that should pass validation) and invalid cases designed to trigger validation errors. This makes it easy to verify that the schema and normalization logic work as expected, and to demonstrate error handling for bad input.

Validation & Integration Testing: The project provides an integration test runner (accessible via a CLI option) that automatically validates all fixtures. It reports which fixtures pass or fail, and details any schema violations or normalization issues. This ensures that any changes to the schemas or code can be quickly tested against a variety of scenarios.

Command-Line Interface (CLI): Offers a convenient CLI built with Python’s argparse. Users can run the tool from the command line with options like --test (to execute the full test suite on sample data) or --preview (to see a quick preview of the normalization process on example input). The CLI makes it easy to interact with the codebase without writing additional scripts or code.

Directory Structure

The repository is organized into modules, each focusing on a specific aspect of the functionality. Key files include:

SmartTravelProject/
├── schemas.py        # JSON schemas for user profile and user query definitions
├── normalizer.py     # Functions for taxonomy and budget normalization
├── validator.py      # Schema validation logic using jsonschema (Draft 7)
├── fixtures.py       # Sample data (valid/invalid profiles and queries) for testing
├── cli.py            # Command-line interface definition (argparse for --test/--preview)
├── README.md         # Project documentation (this file)
└── LICENSE           # License information (placeholder)


(Note: Additional files like __init__.py, configuration files, or a requirements.txt may also be present as needed, but the above shows the primary code modules.)

Installation Instructions

Prerequisites: Ensure you have Python 3.10+ installed, as the codebase uses Python 3.10 features and standard libraries (e.g. dataclasses, argparse).

Dependency: The main external dependency is jsonschema for JSON Schema validation. You can install it via pip:

pip install jsonschema


If this project is cloned from a repository, you can install all requirements (if a requirements.txt is provided) with:

pip install -r requirements.txt


No additional installation steps are required. All other modules used (such as argparse and dataclasses) are part of the Python standard library. Once dependencies are installed, you can run the CLI script or import the modules in your own code.

CLI Usage

The Smart Travel Project comes with a command-line interface to run its features directly. To use the CLI, navigate to the project directory in your terminal. You can run the CLI via the cli.py script. Use the -h or --help flag to see available options:

$ python cli.py --help
usage: cli.py [--test] [--preview]

Options:
  --test     Run validation tests on all sample fixtures (user profiles/queries)
  --preview  Preview normalization on an example user profile and query


You should specify one of the modes (--test or --preview) when running the script:

Test Mode (--test)

Running the tool with the --test flag will execute the validation and normalization on all provided fixture data. This is essentially a self-test to verify that the schema and normalization logic work correctly. It will iterate through each sample profile/query and report the results. For example:

$ python cli.py --test
Running integration tests on sample user profiles and queries...
✔ Fixture 1 (Basic valid profile & query): PASSED
✔ Fixture 2 (Missing required fields): FAILED
   └─ Errors: "age" is a required property; "preferences[2]" is not one of ['relax','foodie','adventure']
✔ Fixture 3 (Invalid budget format): FAILED
   └─ Errors: "budget.amount" must be a number; "budget.currency" must be one of ['USD','EUR','JPY']
✔ Fixture 4 (Valid complex profile & query): PASSED

Test summary: 2 passed, 2 failed


In the above sample output, the test runner validated four fixture cases. It shows which fixtures passed and which failed, and for failures it lists the specific validation errors (such as missing required fields or invalid values). The green checkmarks (✔) indicate each fixture processed; failures include an error summary. This helps developers quickly spot issues in the data or changes in the schema logic.

Preview Mode (--preview)

Using the --preview flag will demonstrate the normalization process on a sample input (for instance, using one of the valid fixture profiles/queries or a hard-coded example). This mode is useful to see how raw user input is transformed and validated. For example:

$ python cli.py --preview
*** Previewing normalization for a sample user profile and query ***

Original User Profile (input):
{
  "name": "Alice",
  "age": 29,
  "preferences": ["chill", "culinary", "adventure"]
}

Original Travel Query (input):
{
  "destination": "Paris",
  "duration_days": 7,
  "budget": {"amount": 1000, "currency": "EUR"}
}

Validating input against schema... OK

Normalized User Profile:
{
  "name": "Alice",
  "age": 29,
  "preferences": ["relax", "foodie", "adventure"]
}

Normalized Travel Query:
{
  "destination": "Paris",
  "duration_days": 7,
  "budget": {"amount": 1200, "currency": "USD"}
}


In this preview example, the user’s free-form preferences "chill" and "culinary" were normalized to the standard categories "relax" and "foodie". The travel query’s budget of 1000 EUR was converted to 1200 USD using a stubbed exchange rate (for demonstration). The preview confirms that the input data passes schema validation and shows the final dataclass objects (here represented as JSON-like dicts) that the application would use. This gives a quick insight into the system’s behavior without requiring any custom input from the user.

Modules Summary

This section provides a brief overview of each module in the codebase and their responsibilities:

schemas.py

Contains the JSON Schema definitions for the user profile and user query data structures. Two primary schema dictionaries (or JSON files) are defined: one for user_profile and one for user_query. These schemas specify required fields (for example, a profile might require name, age, etc., and a query might require destination, budget, etc.), data types (e.g. strings, integers, objects), and in some cases value restrictions (such as an enumeration of allowed preference categories or currency codes). By centralizing the schema here, the rest of the code can validate input data against a single source of truth for structure. The schemas adhere to the Draft 7 specification of JSON Schema.

normalizer.py

Implements the normalization logic for user inputs. This module maps raw input values to standardized forms:

Preference Taxonomy: Defines a mapping of various free-text preference keywords to a controlled vocabulary. For example, this mapping may be a dictionary like {"chill": "relax", "relaxation": "relax", "culinary": "foodie", "food": "foodie", ...}. When a user profile’s preference list is processed, each preference string is looked up and replaced with the normalized category (if a mapping exists), otherwise it may be left as-is or flagged if unknown. The result is a consistent set of preference tags such as "relax", "foodie", "adventure", etc.

Budget Conversion: Provides functionality to normalize budget information. If a budget is given in a currency different from the system’s base or preferred currency, this module uses a stubbed conversion rate to convert the amount. For example, it might include a small currency table like {"USD": 1.0, "EUR": 1.2, "JPY": 0.009} indicating relative values to USD. A budget of {"amount": 1000, "currency": "EUR"} would thus be converted to {"amount": 1200, "currency": "USD"} in this example. (The exchange rates in the code are fixed samples for demonstration and can be updated to real values or API calls in the future.)

After normalization, this module can output standardized data which can be further processed or directly used for generating travel recommendations.

validator.py

Handles validation of user data against the schemas. This module uses the jsonschema library’s Draft7Validator to check that a given user profile or query matches the expected format defined in schemas.py. Key aspects of this module:

It likely provides functions such as validate_profile(data) or validate_query(data) that run the validator on the input data.

It utilizes Draft7Validator.iter_errors(instance) to gather all validation errors in the instance. This means if multiple fields are wrong or missing, the function will collect each error message rather than stopping at the first error. This is very useful for debugging user input or schema issues, as it gives a full report of what’s wrong.

The validator may format these errors into readable messages, possibly including the field path and a description of the problem (e.g. "age": expected integer but got string, or "destination": field is required).

If the data is valid, the validator returns successfully (possibly returning the data itself or a True value), and then the data can be passed on to the normalizer. Often, validation might be done before normalization (to ensure required fields exist and are of correct type) and possibly also after normalization (to ensure the normalized data conforms to any stricter schema, such as preferences now being one of the allowed categories).

fixtures.py

Provides sample data to test and demonstrate the system. This module might contain several variables or data structures representing example user_profile and user_query inputs:

Valid examples: e.g. profile_valid_1, query_valid_1, etc., which contain all required fields in correct format. There may be different scenarios, like a minimal valid profile, a full detailed profile, etc.

Invalid examples: e.g. profile_missing_age, query_invalid_budget, etc., which intentionally break the schema rules (missing a field, wrong data type, unsupported currency, etc.) to test that the validator catches these errors.

The fixtures are used by the test runner (via cli.py --test) to automatically verify how the system handles each case. This module makes it easy to extend the test coverage by simply adding new fixture data. It also serves as documentation by example, illustrating what valid input data looks like.

cli.py

Implements the command-line interface for the project. This is the entry-point script that ties everything together for end-users. It uses the argparse library to define available options:

--test: triggers the routine that loads all fixtures and runs validations (and possibly normalizations) on them. The CLI will likely call functions in validator.py for each fixture and report the results to the console, as shown in the example output above. It might count passes/failures and highlight any errors found.

--preview: runs a demonstration of the normalization and validation process on a sample input. The CLI might load a specific example from fixtures.py (or define one inline) and then use validator.py and normalizer.py to validate and normalize it. The resulting output is printed to the console in a formatted way so that users can see the changes from input to normalized output.

The CLI ensures that exactly one of the modes is chosen (to avoid confusion). It also handles basic things like printing the help message, so users know how to use the tool.

This module makes use of other components: it imports the schemas, uses the validator for checking data, uses the normalizer for conversions, and uses the fixtures for test data. It orchestrates these pieces depending on the CLI arguments.

Extensibility Notes

The Smart Travel Project is designed with clarity and extensibility in mind. Here are a few ways you can extend or customize the system to fit new requirements:

Adding More Preferences or Categories: To support additional user preferences (or synonyms) in the normalization process, update the mapping in normalizer.py. For example, if you want to recognize "nightlife" as a synonym for a category "party", you would add an entry like "nightlife": "party" in the preferences mapping. Also consider updating the JSON schema (if it restricts preferences to a set list) to include any new category values. The system will then automatically translate new keywords to their normalized category when processing profiles.

Adding New Schema Fields: If you need to capture more information in the user profile or query (for example, a travel season preference, or preferred transportation mode, etc.), you should update the schema definitions in schemas.py. Add the new field with its expected type and constraints (and mark it required if necessary). Then, adjust other modules if needed: for instance, update normalizer.py if the new field requires special normalization (e.g. handling a new currency type or a new kind of preference). Also, update fixtures.py to include this field in sample data (both valid and invalid cases) to ensure your tests cover it. The modular structure should contain the impact of changes mostly to these spots.

Integrating Real Currency Conversion: The current budget normalization uses hard-coded exchange rates for simplicity. To use real-world currency conversion, you could integrate an external API or a library. For example, you might use a service like OpenExchangeRates or an open-source library to fetch current rates. This would involve modifying the budget conversion logic in normalizer.py to look up the latest rate instead of a static table. Additionally, you might expand the currency support beyond the current examples (USD, EUR, JPY) to any currency code. Remember to handle API failures or add caching as needed, since external calls can fail or slow down the process. With real conversion, your normalized output will be more dynamic and accurate.

Enhancing Validation Rules: JSON Schema is very powerful. If you need stricter validation (for example, ensuring an age is within a reasonable range, or a trip duration is positive), you can add those rules to the schema (using validation keywords like minimum, maximum, pattern, etc.). The jsonschema library will then automatically enforce them. If you add custom validation logic outside the schema (such as cross-field validation), you can incorporate that in validator.py after the schema validation step.

Extending CLI Functionality: The CLI can be extended with new commands or options. For instance, you might add a new mode that allows users to input their own profile/query via a file or prompt, and then see the validation/normalization result. This could be done by adding a new argparse argument (e.g. --run FILE.json or similar) and writing a handler that reads the input, calls validation and normalization, and prints results or even generates a travel plan. The current structure is a good foundation for expansion.

License

This project is released under an open-source license (placeholder). See the LICENSE file for more details. (For now, the license information is to be determined and will be updated in this section.)