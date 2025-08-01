function Ensure-PythonVenvActive {
    param (
        [Parameter(Mandatory=$true)]
        [string]$VenvPath
    )

    # Check if the standard virtual environment variable is already set
    if (-not ($env:VIRTUAL_ENV)) {
        $activationScript = Join-Path -Path $VenvPath -ChildPath "Scripts\Activate.ps1"

        if (Test-Path $activationScript) {
            try {
                # Dot-source the activation script to apply it to the current scope
                . $activationScript
                Write-Host "Python virtual environment at '$VenvPath' is now active." -ForegroundColor Green
            }
            catch {
                Write-Error "Failed to activate the virtual environment at '$VenvPath'."
                # Stop the script if activation fails, as subsequent commands might depend on it
                exit 1
            }
        }
        else {
            Write-Error "Activation script not found at '$activationScript'. Please check the path."
            exit 1
        }
    }
    else {
        # If already active, just print a confirmation message
        Write-Host "Python virtual environment is already active: $($env:VIRTUAL_ENV)" -ForegroundColor Cyan
    }
}

# # Load .env file
# get-content .env | foreach {
#     $name, $value = $_.split('=')
#     set-content env:\$name $value
# }

# Read the .env file line by line
Get-Content .env | ForEach-Object {
    # Check if the line is not empty and contains an equals sign
    if (-not [string]::IsNullOrWhiteSpace($_) -and $_.Contains('=')) {
        # Remove the "export " prefix if it exists
        $line = $_.Trim() -replace '^export ',''

        # Split the line into a key and value at the first '='
        $key, $value = $line.Split('=', 2)

        # Remove any surrounding quotes from the value
        $value = $value.Trim('"').Trim("'")

        # Set the environment variable for the current session
        Write-Host "Setting environment variable: $key"
        Set-Item -Path "env:$key" -Value $value
    }
}

$myVenvPath = ".\.venv" # Or the specific path to your venv
Ensure-PythonVenvActive -VenvPath $myVenvPath

# .\venv\Scripts\Activate.ps1

uvicorn main:app --reload --port 8989
