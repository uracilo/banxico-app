# 💵 Banxico USD/MXN Exchange Streamlit App


A **Streamlit** application that queries the **Banxico API** to display:

1. Current FIX exchange rate (USD → MXN).  
2. Average of the last **15 and 30 days**.  
3. Historical values of the last **10 days**.  

The app includes:
- **Optimized API calls** to minimize usage and avoid reaching limits.  
- **Intelligent caching**: short TTL for latest rates (2 min), longer TTL for historical data (10 min).  
- **Rate limit alerts** for both Oportuna and Historica endpoints, including warnings at 50% and 75-85% of limits.  
- **Dark theme card UI** with responsive design.  
- **Result caching** for performance improvements.  

---

## ⚡ Requirements

- Python 3.10+ (if running locally without Docker).  
- A valid **Banxico token** → obtainable from Banxico’s developer portal.  

---

## 🚀 Local Installation (without Docker)

```bash
# Clone the repository
git clone https://github.com/your_username/banxico-app.git
cd banxico-app

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Export the token
export BANXICO_TOKEN=your_token_here

# Run the app
streamlit run app.py
```

The app will be available at 👉 [http://localhost:8501](http://localhost:8501).  

---

## 🐳 Run with Docker Compose

### 1. Configure the token
Create a **.env** file in the project root:  
```env
BANXICO_TOKEN=your_token_here
```

### 2. Start the container
```bash
docker-compose up --build
```

Open in 👉 [http://localhost:8501](http://localhost:8501).  

---

## 🔄 GitHub Actions Pipeline

This repo includes a workflow in `.github/workflows/build.yml` that:  
- Builds the Docker image in GitHub Actions on every push to `main`.  
- Validates the `Dockerfile`.  

> ⚠️ The image is **not pushed to any registry**: deployment is handled locally with `docker-compose`.  

---

## 🛠️ Main Functions

- **`fetch_oportuna_fix()`** → Fetches the most recent FIX exchange rate (USD→MXN).  
- **`fetch_historica_fix(start, end)`** → Retrieves historical exchange rates in a single call to cover all calculations.  
- **`avg_last_n_points(df, n)`** → Computes the average of the last `n` data points.  
- **`check_rate_alerts(kind)`** → Alerts when API requests reach 50%, 75%, or daily thresholds.  
- **Optimized caching** → Avoids repeated API calls while keeping data up-to-date.  

---

## 📊 API Usage & Estimated Daily Calls

| Data Requested           | Endpoint   | Calls per refresh | Refreshes/day (15 min) | Total calls/day |
|--------------------------|------------|-----------------|-----------------------|----------------|
| Current USD→MXN FIX      | Oportuna   | 1               | 96                    | 96             |
| Historical last 120 days | Historica  | 1               | 96                    | 96             |

> Total daily calls = 192, safely below Banxico's daily limits (Oportuna: 40,000, Historica: 10,000).  

---

## 📊 UI Example

The app displays modern cards showing:  
- Current FIX rate (USD → MXN).  
- Averages for the last 15 and 30 days.  
- Last 10 historical records.  


---
# Banxico App -- AWS Infrastructure with CloudFormation


------------------------------------------------------------------------

## 📦 Prerequisites

-   **AWS CLI** installed and configured with valid credentials and
    default region.\
    👉 [Install AWS
    CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
-   A valid **EC2 Key Pair** created in the target AWS region.
-   Access to the **custom AMI** that includes Docker, Docker Compose,
    and GitHub Actions Runner.\
    👉 If you don't have access, request it at
    **benjamin.casazza@gmail.com**.
-   Sufficient IAM permissions to create:
    -   VPC, Subnet, Route Tables, Internet Gateway
    -   EC2 Instance, Elastic IP
    -   IAM Role and Instance Profile
    -   Security Groups
-   Ensure your AWS account has **Elastic IP quota** available (by
    default: 5 per region).

------------------------------------------------------------------------

## 🚀 Create the stack

Run the following command to create the stack:

``` bash
aws cloudformation create-stack   --stack-name banxico-app   --template-body file://infra/public.yml   --parameters       ParameterKey=AmiId,ParameterValue=ami-02b2f08ba7a69a001       ParameterKey=InstanceType,ParameterValue=t3.small       ParameterKey=KeyPair,ParameterValue=test       ParameterKey=SSHCidr,ParameterValue=201.123.45.67/32       ParameterKey=AppDir,ParameterValue=/opt/banxico   --capabilities CAPABILITY_NAMED_IAM
```

📌 **Parameter notes**: - `AmiId`: The ID of the custom AMI with
pre-installed environment. - `InstanceType`: EC2 instance type (e.g.,
`t3.micro`, `t3.small`). - `KeyPair`: The name of your EC2 key pair. -
`SSHCidr`: The CIDR range allowed for SSH access (recommended: your
public IP with `/32`). - `AppDir`: Path in the AMI where the app and
`docker-compose.yml` reside (default: `/opt/banxico`).

------------------------------------------------------------------------

## 🔎 Get stack outputs

After creation, retrieve the public IP and application URL:

``` bash
aws cloudformation describe-stacks   --stack-name banxico-app   --query "Stacks[0].Outputs"
```

Expected outputs: - `AppPublicIP`: Public Elastic IP of the instance. -
`AppURL`: Public URL to access the application (HTTP on port 80).

------------------------------------------------------------------------

## 🗑️ Delete the stack

When you want to tear everything down:

``` bash
aws cloudformation delete-stack --stack-name banxico-app
aws cloudformation wait stack-delete-complete --stack-name banxico-app
```

⚠️ **Note**:\
If you set `DeletionPolicy: Retain` on the Elastic IP, the IP will
**not** be released automatically.\
To release it manually:

``` bash
aws ec2 describe-addresses --query "Addresses[*].{ID:AllocationId,IP:PublicIp}"
aws ec2 release-address --allocation-id <allocation-id>
```

------------------------------------------------------------------------

## ✅ Deployment checklist

-   [ ] Valid Key Pair created in AWS region.\
-   [ ] Access to custom AMI (or request from
    **benjamin.casazza@gmail.com**).\
-   [ ] Elastic IP quota available in your AWS account.\
-   [ ] IAM user/role has `cloudformation:*`, `ec2:*`, and
    `iam:PassRole` permissions.\
-   [ ] AWS CLI configured with proper credentials and region.\
-   [ ] Update `SSHCidr` parameter to your IP (not `0.0.0.0/0`) for
    security.

------------------------------------------------------------------------

## 💰 Cost considerations

-   **EC2 instance**: hourly charge depending on instance type.\
-   **Elastic IP**: free when associated with a running instance;
    charged if allocated but unused.\
-   **Data transfer**: standard AWS rates for traffic in/out of the
    instance.

------------------------------------------------------------------------

## 📧 Contact

For questions or to request access to the custom AMI, contact
**benjamin.casazza@gmail.com**.

## 📜 License

MIT License © 2025
