import streamlit as st
import streamlit.components.v1 as components
import base64

# Convert the sound file to base64
def get_base64_sound(file_path):
    with open(file_path, "rb") as sound_file:
        data = sound_file.read()
        return base64.b64encode(data).decode()

# Convert 'beep-beep.wav' and 'cheerful.wav' files to base64 strings
beep_sound_base64 = get_base64_sound("Learn/beep-beep.wav")
cheerful_sound_base64 = get_base64_sound("Learn/cheerful.wav")

# Python variable 'word'
word = "How are you"
initial_word_score = len(word) - word.count(" ")  # Initialize word_score based on the length of the word

# Initialize session state variables
if 'final_score' not in st.session_state:
    st.session_state.final_score = -1  # Initial value for final score, indicating no score yet

if 'next_button' not in st.session_state:
    st.session_state.next_button = False  # Initialize next_button flag

# Main App
def main():
    # Check if score update is triggered by JavaScript fetch
    def refresh():
        if st.session_state.final_score != -1:
            st.write(f"Final Score: {st.session_state.final_score}")
            st.session_state.next_button = True  # Enable the next button
            st.session_state.final_score = -1  # Reset final_score for future use

    # Create an HTML component with JavaScript to handle input, color, and deletion of text
    components.html(
        f"""
        <html>
            <head>
                <style>
                    /* Increase font size to 14px */
                    body {{
                        font-size: 18px;
                    }}

                    /* Align display area and score on the same line */
                    #container {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 10px;
                    }}

                    #displayArea {{
                        flex: 1;
                        text-align: left;
                    }}

                    #scoreArea {{
                        flex-shrink: 0;
                        text-align: right;
                        margin-left: 20px;
                    }}

                    /* Center input box and add margin to the top */
                    #textInput {{
                        width: 100%;
                        margin-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <div id="container">
                    <p id="displayArea">{''.join('_' if c == ' ' else '-' for c in word)}</p> <!-- Display underscores for spaces and dashes for other characters -->
                    <p id="scoreArea">Score: {initial_word_score}</p> <!-- Display the initial word score -->
                </div>
                <input type="text" id="textInput" placeholder="Enter some text" oninput="checkText()" />

                <audio id="alarmSound" src="data:audio/wav;base64,{beep_sound_base64}" preload="auto"></audio> <!-- Beep alarm sound -->
                <audio id="cheerfulSound" src="data:audio/wav;base64,{cheerful_sound_base64}" preload="auto"></audio> <!-- Cheerful sound -->

                <script>
                    // JavaScript variables
                    const word = "{word}".toLowerCase(); // Convert the word to lowercase for case-insensitive comparison
                    let wordScore = {initial_word_score}; // Initialize wordScore with the length of the word
                    let timer = null;
                    let alarmPlayed = false; // To prevent multiple sound overlaps
                    let cheerPlayed = false; // To play cheerful sound only once

                    function checkText() {{
                        // Get the value from the input field and convert it to lowercase for case-insensitive comparison
                        var inputText = document.getElementById("textInput").value.toLowerCase();
                        var updatedText = "";
                        var lastIndex = 0;
                        var allMatch = true;

                        // Iterate over each character in the word
                        for (let i = 0; i < word.length; i++) {{
                            if (i < inputText.length) {{
                                if (inputText[i] === word[i] && allMatch) {{
                                    // Matching character, keep it green
                                    updatedText += '<span style="color: green;">' + inputText[i] + '</span>';
                                    lastIndex = i + 1;
                                    alarmPlayed = false; // Reset alarm
                                }} else {{
                                    // Non-matching character, make it red, stop further matching, and play the alarm sound
                                    updatedText += '<span style="color: red;">' + inputText[i] + '</span>';
                                    if (!alarmPlayed) {{
                                        document.getElementById("alarmSound").play(); // Play the alarm sound
                                        alarmPlayed = true; // Prevent multiple plays
                                        if (wordScore > 0) {{
                                            wordScore--; // Deduct one point for the wrong character if score is above zero
                                        }}
                                    }}
                                    allMatch = false;
                                }}
                            }} else {{
                                // Display underscores for spaces and dashes for other characters
                                updatedText += word[i] === ' ' ? '_' : '-';
                            }}
                        }}

                        // Update the score display
                        document.getElementById("scoreArea").innerHTML = "Score: " + wordScore;

                        // Display the formatted text
                        document.getElementById("displayArea").innerHTML = updatedText;

                        // Check if the entire input matches the word
                        if (inputText === word && !cheerPlayed) {{
                            document.getElementById("cheerfulSound").play();
                            cheerPlayed = true; // Play cheerful sound only once

                            // Disable the input field since the input matches the word
                            document.getElementById("textInput").disabled = true;

                            // Send the final wordScore to Streamlit
                            fetch('/?final_score=' + wordScore, {{method: 'POST'}})
                        }}

                        // Clear the previous timer if it exists
                        if (timer) {{
                            clearTimeout(timer);
                        }}

                        // Set a new timer to remove the red characters after 0.5 seconds
                        timer = setTimeout(function() {{
                            // Only keep the matching part of the input text
                            document.getElementById("textInput").value = document.getElementById("textInput").value.substring(0, lastIndex);

                            // Move the cursor to the end of the input
                            document.getElementById("textInput").focus();
                            document.getElementById("textInput").setSelectionRange(lastIndex, lastIndex);
                        }}, 500);
                    }}
                </script>
            </body>
        </html>
        """,
        height=250  # Adjust height as needed
    )

    def refresh():
        if st.session_state.final_score != -1:
            st.write(f"Final Score: {st.session_state.final_score}")
            st.session_state.next_button = True  # Enable the next button
            st.session_state.final_score = -1  # Reset final_score for future use
    # Logic to display the next button based on session state
    
    refresh()
    
    if st.session_state.next_button:
        if st.button('Next'):
            st.write("Next action executed! Proceeding to the next word or step.")
            st.session_state.next_button = False  # Reset the button state for future use
    else:
        st.button('Next', disabled=True)

if __name__ == '__main__':
    main()
