pushd
./build.ps1
docker push 051055614445.dkr.ecr.us-east-1.amazonaws.com/quick-api-repo:latest
cd tf
terraform apply --auto-approve
popd