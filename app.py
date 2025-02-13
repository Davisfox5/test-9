To create a React-based web application with a Flask backend, we will need to create a few files. 

First, let's create the Flask backend. We will need two files: `app.py` for the Flask application and `requirements.txt` for the Python dependencies.

```branch=main
path=backend/app.py
```
```python
from flask import Flask, jsonify
import random
import string

app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate_word():
    letters = string.ascii_lowercase
    random_word = ''.join(random.choice(letters) for i in range(10))
    return jsonify({'word': random_word})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```
```branch=main
path=backend/requirements.txt
```
```
flask
```

Next, let's create the React frontend. We will need three files: `package.json` for the Node.js dependencies, `src/App.js` for the React application, and `.env` for the environment variables.

```branch=main
path=frontend/package.json
```
```json
{
  "name": "random-word-generator",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "react": "^17.0.2",
    "axios": "^0.21.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```
```branch=main
path=frontend/src/App.js
```
```jsx
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [word, setWord] = useState('');

  const generateWord = () => {
    axios.get(process.env.REACT_APP_BACKEND_URL + '/generate')
      .then(response => {
        setWord(response.data.word);
      });
  };

  return (
    <div>
      <button onClick={generateWord}>Generate Word</button>
      <p>{word}</p>
    </div>
  );
}

export default App;
```
```branch=main
path=frontend/.env
```
```
REACT_APP_BACKEND_URL=http://localhost:5000
```

To host this application on AWS or Azure, you would typically use a service like AWS Elastic Beanstalk or Azure App Service. The cost would depend on the size of the instances you choose and the amount of traffic your application receives. As a rough estimate, you could expect to pay around $30-50 per month for a small to medium-sized application.

```run
echo "Estimated hosting cost: $30-50/month"
```

summary=Created a React-based web application with a Flask backend. Estimated hosting cost on AWS or Azure is around $30-50/month.