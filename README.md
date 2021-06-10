# Weather chatbot assignment

In this assignment I am tasked to create chatbot which will provide real weather report for given location.

## Setup

Needs private weather api (https://app.tomorrow.io/home) token defined in .env file. 
```dotenv
CLIMACELL_API_KEY=token
```

```
#get .env file with weather api token
docker-compose up -d --build
```

## Assumptions

- User asks for weather using words that are similar / close to word weather (sunny, cloudy, ...)
- Location must be specified as name of City or Country

## Future plan

- Secure connections
- Spacy entity and trained DIETclassifier are weak when detecting less known cities. Needs more data or better city entity recognition.
