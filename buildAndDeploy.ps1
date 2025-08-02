Push-Location
./buildImage.ps1
docker push 051055614445.dkr.ecr.us-east-1.amazonaws.com/quick-api-repo:latest
Set-Location tf
terraform apply --auto-approve
Pop-Location