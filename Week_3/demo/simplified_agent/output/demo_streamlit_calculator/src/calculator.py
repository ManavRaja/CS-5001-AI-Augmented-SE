import streamlit as st
import numpy as np

def main():
    st.title("Streamlit Calculator")

    # Sidebar for operation selection
    operation = st.sidebar.selectbox(
        "Select Operation",
        ["Addition", "Subtraction", "Multiplication", "Division", "Exponentiation", "Square Root", "Logarithm"]
    )

    # Input fields
    col1, col2 = st.columns(2)

    with col1:
        num1 = st.number_input("First Number", value=0.0)

    with col2:
        if operation in ["Addition", "Subtraction", "Multiplication", "Division", "Exponentiation"]:
            num2 = st.number_input("Second Number", value=0.0)
        else:
            num2 = 0.0

    # Perform calculation
    result = None
    if operation == "Addition":
        result = num1 + num2
    elif operation == "Subtraction":
        result = num1 - num2
    elif operation == "Multiplication":
        result = num1 * num2
    elif operation == "Division":
        if num2 != 0:
            result = num1 / num2
        else:
            st.error("Cannot divide by zero!")
    elif operation == "Exponentiation":
        result = num1 ** num2
    elif operation == "Square Root":
        if num1 >= 0:
            result = np.sqrt(num1)
        else:
            st.error("Cannot calculate square root of negative number!")
    elif operation == "Logarithm":
        if num1 > 0:
            result = np.log(num1)
        else:
            st.error("Cannot calculate logarithm of non-positive number!")

    # Display result
    if result is not None:
        st.success(f"Result: {result}")

if __name__ == "__main__":
    main()
