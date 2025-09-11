#!/bin/bash
set -euo pipefail

# -------- CONFIGURACIÓN --------
SOURCE_REGION="us-east-1"      # Región donde vive la AMI original
DEST_REGION="us-east-1"        # Región donde quieres tu AMI
SOURCE_AMI_ID="ami-XXXXXXXX"   # ID de la AMI compartida
NEW_AMI_NAME="banxico-app-ami" # Nombre de la AMI en tu cuenta

# -------- FUNCIONES --------
check_permissions() {
    echo "🔍 Verificando permisos sobre AMI $SOURCE_AMI_ID..."
    aws ec2 describe-image-attribute \
        --image-id "$SOURCE_AMI_ID" \
        --attribute launchPermission \
        --region "$SOURCE_REGION" || {
        echo "❌ No tienes permisos sobre la AMI. Pide al dueño que te la comparta."
        exit 1
    }
    echo "✅ Tienes permisos para usar esta AMI."
}

check_snapshots() {
    echo "🔍 Buscando snapshots asociados a la AMI..."
    SNAPSHOT_IDS=$(aws ec2 describe-images \
        --image-ids "$SOURCE_AMI_ID" \
        --region "$SOURCE_REGION" \
        --query "Images[0].BlockDeviceMappings[].Ebs.SnapshotId" \
        --output text)

    echo "📦 Snapshots encontrados: $SNAPSHOT_IDS"
}

copy_ami() {
    echo "🚀 Copiando AMI a tu cuenta en región $DEST_REGION..."
    COPY_RESULT=$(aws ec2 copy-image \
        --source-image-id "$SOURCE_AMI_ID" \
        --source-region "$SOURCE_REGION" \
        --region "$DEST_REGION" \
        --name "$NEW_AMI_NAME" \
        --query "ImageId" \
        --output text)

    NEW_AMI_ID=$COPY_RESULT
    echo "✅ Copia iniciada: $NEW_AMI_ID"
}

wait_for_available() {
    echo "⏳ Esperando a que la AMI $NEW_AMI_ID esté disponible..."
    aws ec2 wait image-available --image-ids "$NEW_AMI_ID" --region "$DEST_REGION"
    echo "🎉 La AMI ya está lista: $NEW_AMI_ID"
}

# -------- MAIN --------
check_permissions
check_snapshots
copy_ami
wait_for_available
