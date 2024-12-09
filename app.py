from flask import Flask, render_template, request, jsonify
from llama_index.llms.groq import Groq
import pandas as pd

app = Flask(__name__)

# Set the Groq API Key
GROQ_API_KEY = "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"

# Initialize the Groq LLM
llm = Groq(
    model="llama3-8b-8192",  # Groq's smaller model for efficient predictions
    api_key=GROQ_API_KEY,
)

def generate_prompt(num_teachers, classrooms, students, books, science_lab, sports_equipment):
    return f"""
    You are an expert educational consultant tasked with creating a budget for a school. 
    Here are the provided details:
    - Number of Teachers Needed: {num_teachers}
    - Classrooms to Renovate: {classrooms}
    - Underprivileged Students: {students}
    - Library Books Required: {books}
    - Science Lab Required: {'Yes' if science_lab else 'No'}
    - Sports Equipment Required: {'Yes' if sports_equipment else 'No'}

    Based on these inputs, calculate and provide an approximate budget in INR with a detailed breakdown of:
    - Teachers' Salaries (Annual)
    - Student Grants
    - Infrastructure (Renovation and Lab Setup)
    - Facilities (Books, Sports Equipment)
    - Annual Maintenance
    Also provide the Total Budget.
    Respond with a formatted table as follows:
    | Category            | Cost (INR)    |
    |---------------------|---------------|
    """

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_budget():
    data = request.json
    try:
        # Generate the prompt
        prompt = generate_prompt(
            data["num_teachers"],
            data["classrooms"],
            data["students"],
            data["books"],
            data["science_lab"],
            data["sports_equipment"]
        )
        
        # Get response from Groq LLM
        response = llm.complete(prompt)
        response_text = response.text  # Extract text attribute
        
        # Parse the response into a table
        lines = response_text.strip().split("\n")[2:]  # Skip header and separator lines
        table_data = []
        for line in lines:
            if "|" in line:  # Check for valid table rows
                columns = line.split("|")[1:3]  # Extract only relevant columns
                category = columns[0].strip()  # Category column
                cost = columns[1].strip().replace(",", "")  # Clean the cost column
                if cost.isdigit():  # Ensure the cost is numeric
                    table_data.append({"Category": category, "Cost (INR)": float(cost)})
        
        # Convert to a DataFrame
        df = pd.DataFrame(table_data)
        
        # Calculate the total budget
        total_budget = df["Cost (INR)"].sum()
        
        return jsonify({"table": df.to_dict(orient="records"), "total_budget": total_budget})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
