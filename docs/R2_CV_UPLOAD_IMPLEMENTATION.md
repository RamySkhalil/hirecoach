# R2 CV Upload Implementation

## Overview

This document describes the implementation of Cloudflare R2 storage for CV/resume uploads in the Interviewly ATS system. Candidates can now upload their CVs directly when applying for jobs, with files stored securely in R2.

## Architecture

### Components

1. **R2 Storage Service** (`backend/app/services/r2_storage_service.py`)
   - Handles all R2 operations (upload, delete, signed URLs)
   - Validates file types and sizes
   - Generates unique filenames to prevent collisions
   - Stores files in `Applicants/` folder

2. **Backend API** (`backend/app/routes/ats.py`)
   - Updated `/api/ats/v1/jobs/{job_id}/apply` endpoint
   - Accepts both file uploads and URLs
   - File upload takes precedence over URL

3. **Frontend Form** (`frontend/app/jobs/[jobId]/page.tsx`)
   - Drag-and-drop file upload interface
   - File validation and preview
   - Upload progress indicator
   - Fallback to URL input if no file selected

## Configuration

### Environment Variables

Add these to your `backend/.env` file:

```env
# Cloudflare R2 Configuration
R2_BUCKET_NAME=your-bucket-name
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com  # Optional
R2_PUBLIC_URL=https://your-custom-domain.com  # Optional, for custom CDN
```

### Bucket Setup

1. Create an R2 bucket in Cloudflare dashboard
2. Create a folder named `Applicants/` in the bucket
3. Configure bucket permissions (public read if using public URLs, or use signed URLs)

## File Validation

### Allowed File Types
- PDF (`.pdf`)
- Microsoft Word (`.doc`, `.docx`)
- Text files (`.txt`)

### File Size Limit
- Maximum: 10MB per file

### Validation Flow
1. Frontend validates file type and size before upload
2. Backend re-validates for security
3. Files are stored with unique names to prevent collisions

## API Endpoints

### POST `/api/ats/v1/jobs/{job_id}/apply`

**Request:**
- `Content-Type: multipart/form-data`
- Fields:
  - `candidate_name` (required): string
  - `candidate_email` (required): string
  - `candidate_phone` (optional): string
  - `candidate_location` (optional): string
  - `resume_file` (optional): file upload
  - `resume_url` (optional): string URL

**Response:**
```json
{
  "id": "application-id",
  "job_id": "job-id",
  "candidate_id": "candidate-id",
  "candidate_name": "John Doe",
  "candidate_email": "john@example.com",
  "status": "APPLIED",
  "fit_score": 75.5,
  "applied_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400`: Invalid file type or size
- `404`: Job not found or not open
- `500`: Upload failed
- `503`: R2 service not configured

## File Storage Structure

```
R2 Bucket/
└── Applicants/
    ├── abc123def456.pdf
    ├── xyz789ghi012.docx
    └── ...
```

Files are stored with unique hexadecimal names to prevent collisions and ensure security.

## Security Considerations

1. **File Validation**: Both frontend and backend validate file types and sizes
2. **Unique Filenames**: Prevents overwriting and directory traversal attacks
3. **Content-Type Headers**: Proper MIME types set for all uploads
4. **Error Handling**: Graceful degradation if R2 is not configured
5. **Size Limits**: Prevents DoS attacks via large file uploads

## Error Handling

### Frontend
- File type validation before upload
- File size validation
- Upload progress indicator
- Clear error messages
- Fallback to URL input

### Backend
- Re-validation of all files
- Detailed error messages
- Graceful handling of missing R2 configuration
- Transaction rollback on failure

## Dependencies

### Backend
- `boto3`: AWS SDK for Python (S3-compatible API)
- `botocore`: Core functionality for boto3

Install with:
```bash
pip install boto3 botocore
```

Or add to `requirements.txt`:
```
boto3
botocore
```

## Usage Example

### Frontend (React/Next.js)

```typescript
const formData = new FormData();
formData.append('candidate_name', 'John Doe');
formData.append('candidate_email', 'john@example.com');
formData.append('resume_file', file);

const response = await fetch(`/api/ats/v1/jobs/${jobId}/apply`, {
  method: 'POST',
  body: formData
});
```

### Backend (Python/FastAPI)

```python
from app.services.r2_storage_service import get_r2_service

r2_service = get_r2_service()
if r2_service:
    url = r2_service.upload_file(
        file_content,
        filename="resume.pdf",
        folder="Applicants"
    )
```

## Testing

### Manual Testing Steps

1. **File Upload Test**
   - Navigate to job application page
   - Select a PDF file
   - Verify file preview appears
   - Submit application
   - Check R2 bucket for uploaded file

2. **File Validation Test**
   - Try uploading invalid file type (e.g., `.exe`)
   - Try uploading file > 10MB
   - Verify error messages appear

3. **URL Fallback Test**
   - Don't upload file
   - Enter resume URL
   - Submit application
   - Verify URL is saved

4. **Error Handling Test**
   - Disable R2 configuration
   - Try uploading file
   - Verify graceful error message

## Future Enhancements

1. **File Processing**
   - Extract text from PDFs/DOCs
   - Generate thumbnails
   - OCR for scanned documents

2. **Signed URLs**
   - Generate temporary access URLs for private files
   - Set expiration times

3. **File Management**
   - Delete old files automatically
   - Archive applications after X days
   - Compress files before storage

4. **Analytics**
   - Track upload success/failure rates
   - Monitor storage usage
   - File type distribution

## Troubleshooting

### Common Issues

1. **"R2 service is not configured"**
   - Check environment variables are set
   - Verify R2 credentials are correct
   - Check bucket name and folder exist

2. **"Failed to upload resume"**
   - Check R2 bucket permissions
   - Verify network connectivity
   - Check file size limits

3. **"Invalid file type"**
   - Verify file extension is allowed
   - Check file is not corrupted
   - Ensure MIME type matches extension

## Support

For issues or questions:
1. Check R2 dashboard for upload status
2. Review backend logs for detailed errors
3. Verify environment configuration
4. Test with curl/Postman to isolate issues

