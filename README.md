 # What Should I Eat?

This repository contains two main components:

1. **Function App**: A backend service built using Azure Functions to process images and generate meal suggestions.
2. **Streamlit App**: A frontend application for users to upload images and interact with the meal suggestion system.

---

## Function App

The Function App is responsible for processing uploaded images and generating meal suggestions using AI models.

### Key Features
- Accepts image uploads via the `/process-image` endpoint.
- Uses LangChain and OpenAI models to analyze images and generate detailed descriptions.
- Suggests meals based on the image content, including recipes and nutritional information.

### Endpoints
- **`/process-image`**: Accepts a POST request with an image file and returns a JSON response with meal suggestions.
- **`/chat`**: Accepts a POST request for chat-based interactions with the AI model.

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Azure Function App:
   ```bash
   func start
   ```

### Example Request
```bash
curl -X POST \
  -F "file=@path/to/image.jpg" \
  http://localhost:7071/api/process-image
```

---

## Streamlit App

The Streamlit App provides a user-friendly interface for interacting with the Function App.

### Key Features
- Allows users to upload or capture images.
- Sends images to the Function App for processing.
- Displays meal suggestions and nutritional information.

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run streamlit/app.py
   ```

### Usage
1. Upload or capture an image of your fridge or food items.
2. Click the "Send Image to Endpoint" button.
3. View the meal suggestions and nutritional breakdown.

---

## Folder Structure
```
what_should_i_eat/
├── function_app.py       # Azure Function App backend
├── streamlit/            # Streamlit frontend
├── library/              # Shared utilities and processing logic
├── uploads/              # Temporary storage for uploaded images
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Contributing
Feel free to open issues or submit pull requests for improvements and bug fixes.

---

## License
This project is licensed under the MIT License.