
# Crowdfunding Investment Platform

## **Overview**
This project implements a crowdfunding platform for investment bundles using **Dash**. The platform allows users to select an investment bundle, view its metrics and visualizations, and pledge a predefined amount toward its target. The interface dynamically updates the pledged amounts and redirects users between the selection and pledge pages.

---

## **What Was Lacking in the Original Files**
1. **Logic Improvements**:
   - The original logic file provided metrics (e.g., trailing returns, risk statistics, dividends) but lacked modularity, visualizations, and integration with a user interface (UI).
   - The cost of pledging for each bundle and a mechanism for tracking pledges were missing.
   - No separation of responsibilities for fetching data, calculating metrics, and visualizing results.

2. **UI Requirements**:
   - A user-friendly interface to interact with the investment data was not included.
   - Navigation between pages (bundle selection and pledge pages) needed implementation.
   - Pledge tracking, progress updates, and redirection after pledging were missing.

---

## **Enhancements Made**
### **1. Additional Variables and Functionality**
1. **Dynamic Bundle Costs**:
   - Created a function to calculate the cost for each bundle dynamically based on the sum of ETF prices (last available data) with a 5% markup:
     ```python
     bundle_costs = calculate_bundle_costs()
     ```

2. **Pledge Targets**:
   - Defined a static target pledge amount of $10,000 for each bundle:
     ```python
     bundle_goals = {bundle: 10000 for bundle in bundles.keys()}
     ```

3. **Pledge Tracking**:
   - Added a dictionary to track the amount pledged toward each bundle:
     ```python
     pledge_amounts = {bundle: 0 for bundle in bundles.keys()}
     ```

4. **Active Bundle State**:
   - Introduced a `dcc.Store` component to store the name of the currently selected bundle:
     ```python
     dcc.Store(id="active-bundle", data="")
     ```

### **2. Visualizations**
- Used Plotly to create an interactive bar chart for trailing returns. This visualization is dynamically updated based on the selected bundle.

---

## **UI Implementation**
### **Technologies Used**
- **Dash**: For building the user interface.
- **Plotly**: For interactive visualizations.
- **Pandas**: For data processing and generating metrics.

### **How the UI Works**
1. **First Page: Bundle Selection**
   - Lists three investment bundles (e.g., Bundle 1, Bundle 2, Bundle 3).
   - Displays the amount pledged and progress toward the $10,000 target for each bundle.
   - Allows the user to select a bundle via buttons.

2. **Second Page: Bundle Details**
   - Shows detailed metrics (e.g., trailing returns, risk statistics, and dividends) for the selected bundle.
   - Displays a bar chart visualization of trailing returns.
   - Includes a "Pledge" button with the predefined pledge amount.

3. **Dynamic Pledge Tracking**
   - When the user clicks "Pledge," the platform:
     - Adds the predefined pledge amount to the selected bundle's total.
     - Updates the progress displayed on the first page.
     - Redirects back to the first page.

### **Navigation**
- **To Second Page**:
  - Clicking on a bundle button navigates to the second page.
  - The platform dynamically updates the displayed metrics and visualizations based on the selected bundle.
- **Back to First Page**:
  - Clicking "Pledge" updates the progress and redirects to the first page.

---

## **Code Structure**
### **Key Components**
1. **Logic Functions**:
   - `fetch_data`: Fetches historical data for ETFs in the selected bundle.
   - `calculate_trailing_returns`: Computes trailing returns (1 month, 3 months, etc.).
   - `calculate_risk_statistics`: Computes risk metrics like volatility, Sharpe ratio, and drawdown.
   - `calculate_dividend_info`: Computes dividend yields and payouts.
   - `generate_visualization`: Generates a Plotly bar chart for trailing returns.

2. **Callbacks**:
   - **Unified Navigation and Pledge Callback**:
     - Combines the logic for navigating between pages and handling pledges.
     - Uses `dash.callback_context` to identify whether the user clicked a bundle button or the "Pledge" button.
     - Updates outputs for both the pages and pledge summary dynamically.

3. **Layout**:
   - Two primary pages:
     - **Page 1 (Bundle Selection)**: Displays the bundles, pledge summaries, and progress.
     - **Page 2 (Bundle Details)**: Shows metrics, visualizations, and pledge functionality.

---

## **What the UI Does**
1. **Bundle Selection**:
   - Allows users to view the investment bundles, their progress, and total pledges.
   - Users can select a bundle to view its detailed metrics.

2. **View Bundle Metrics**:
   - Displays key metrics for the selected bundle:
     - Trailing returns.
     - Risk statistics (volatility, Sharpe ratio, max drawdown).
     - Dividend information.

3. **Pledge Functionality**:
   - Automatically calculates and displays the pledge amount for the selected bundle.
   - Updates the pledged amount and progress dynamically.

4. **Dynamic Navigation**:
   - Automatically redirects between the selection page and the pledge details page based on user interactions.

---

## **How to Run the App**
1. Install the required Python libraries:
   ```bash
   pip install dash plotly pandas
   ```
2. Run the `dash_app.py` file:
   ```bash
   python dash_app.py
   ```
3. Open the app in your browser at `http://127.0.0.1:8050`.

---

## **Future Improvements**
- Add error handling for missing or invalid data.
- Introduce user authentication to track individual pledges.
- Enable dynamic creation of bundles with customizable ETFs.

---

