Write-Host "Getting token..." -ForegroundColor Green
$loginResponse = Invoke-WebRequest -Uri "http://localhost:8002/api/users/token" -Method Post -Body @{
    username = "admin"
    password = "password"
} -ContentType "application/x-www-form-urlencoded"

$tokenData = $loginResponse.Content | ConvertFrom-Json
$token = $tokenData.access_token

Write-Host "Token received: $token" -ForegroundColor Green
Write-Host "Creating paper..." -ForegroundColor Green

$paperData = @{
    title = "PowerShell Test Paper"
    authors = "PowerShell Test Author"
    journal = "PowerShell Test Journal"
    year = 2023
    doi = "10.1234/ps-test"
    abstract = "This is a test paper created with PowerShell"
    tags = @("PowerShellTest", "AutomationTest")
}

$paperJson = $paperData | ConvertTo-Json

$createResponse = Invoke-WebRequest -Uri "http://localhost:8002/api/papers/" -Method Post -Headers @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
} -Body $paperJson

$paper = $createResponse.Content | ConvertFrom-Json

Write-Host "Paper created successfully!" -ForegroundColor Green
Write-Host "ID: $($paper.id)" -ForegroundColor Green
Write-Host "Title: $($paper.title)" -ForegroundColor Green
Write-Host "Authors: $($paper.authors)" -ForegroundColor Green
Write-Host "DOI: $($paper.doi)" -ForegroundColor Green
Write-Host "Tags: $($paper.tags -join ', ')" -ForegroundColor Green

Write-Host "Getting paper list..." -ForegroundColor Green
$listResponse = Invoke-WebRequest -Uri "http://localhost:8002/api/papers" -Method Get -Headers @{
    "Authorization" = "Bearer $token"
}

$papers = $listResponse.Content | ConvertFrom-Json
Write-Host "Retrieved $($papers.Count) papers" -ForegroundColor Green

Write-Host "Test complete" -ForegroundColor Green 