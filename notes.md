# Notes for myself

- For package-ability, a template class with abstract methods that user implements for their DB access

  - then they pass an instance of that class in to a generic `rate_limiter` constructor or function, which contains the desired rate limiting functions 

  - need to enforce strict typing on the data access; each limiter has slightly different returns