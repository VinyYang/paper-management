@echo off
echo Getting authentication token...
curl -X POST http://localhost:8002/api/users/token -d "username=admin&password=password" -v

echo Using token to create paper...
set /p token=Please enter the token from above:

curl -X POST http://localhost:8002/api/papers/ -H "Authorization: Bearer %token%" -H "Content-Type: application/json" -d "{\"title\":\"Curl Test Paper\",\"authors\":\"Test Author\",\"journal\":\"Test Journal\",\"year\":2023,\"doi\":\"10.1234/curl-test\",\"abstract\":\"This is a test paper created using curl\",\"tags\":[\"CurlTest\"]}" -v

echo Test complete 