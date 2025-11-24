# CV File Format Support

## Supported Formats

The CV Analyzer supports the following file formats:

### ✅ Supported

1. **PDF (.pdf)** - Recommended
   - Best for preserving formatting
   - Universal compatibility
   - Parsed using PyPDF2

2. **Microsoft Word (.docx)** - Recommended
   - Modern Word format (Office 2007+)
   - Preserves document structure
   - Parsed using python-docx

3. **Plain Text (.txt)**
   - Simple text files
   - No formatting preserved
   - Direct text reading

### ❌ Not Supported

1. **Old Word Format (.doc)**
   - Legacy format (Office 97-2003)
   - **Why?** Different binary format incompatible with python-docx
   - **Solution**: Save as .docx in Word (File → Save As → Word Document .docx)

## File Requirements

- **Maximum Size**: 10MB
- **Encoding**: UTF-8 (for .txt files)
- **Language**: English and Arabic supported

## Converting .doc to .docx

If you have a `.doc` file:

### Option 1: Microsoft Word
1. Open the file in Microsoft Word
2. Click `File → Save As`
3. Choose format: `Word Document (.docx)`
4. Save

### Option 2: LibreOffice/OpenOffice
1. Open the file
2. Click `File → Save As`
3. Choose format: `Microsoft Word 2007-365 (.docx)`
4. Save

### Option 3: Online Converter
- [CloudConvert](https://cloudconvert.com/doc-to-docx)
- [Zamzar](https://www.zamzar.com/convert/doc-to-docx/)
- [Online-Convert](https://document.online-convert.com/convert-to-docx)

## Best Practices

### For Best Analysis Results

1. **Use PDF or DOCX**
   - Better structure preservation
   - More accurate parsing

2. **Keep Formatting Simple**
   - Standard fonts
   - Clear headings
   - Bullet points for lists
   - No complex tables or graphics

3. **Structure Your CV**
   - Clear sections (Experience, Education, Skills)
   - Consistent formatting
   - No images or graphics overlaying text

4. **File Size**
   - Keep under 10MB
   - Remove unnecessary images
   - Compress if needed

## Error Messages

### "File type not supported"
- **Cause**: Wrong file extension
- **Fix**: Convert to .pdf, .docx, or .txt

### "File is not a Word file, content type is 'application/vnd.openxmlformats...'"
- **Cause**: Trying to upload .doc (old format)
- **Fix**: Convert to .docx

### "File too large"
- **Cause**: File exceeds 10MB
- **Fix**: 
  - Remove images/graphics
  - Compress PDF
  - Convert to .docx

### "Failed to extract text"
- **Cause**: Corrupted file or unusual format
- **Fix**: 
  - Try re-saving the file
  - Convert to different format
  - Try PDF format

## Technical Details

### Libraries Used

- **PyPDF2 (3.0.1)**: PDF text extraction
- **python-docx (1.1.0)**: DOCX parsing
- **Built-in**: TXT reading

### Limitations

1. **Images**: Text in images not extracted (use OCR separately if needed)
2. **Complex Layouts**: Multi-column layouts may have parsing issues
3. **Embedded Files**: Only main document text extracted
4. **Macros**: Not executed or parsed
5. **Old Formats**: .doc, .rtf, .odt not supported

## Future Support

Planned for future versions:

- ⏳ OCR for scanned PDFs
- ⏳ RTF format support
- ⏳ ODT (OpenDocument) support
- ⏳ Batch upload (multiple files)
- ⏳ Direct LinkedIn import

## Need Help?

If you're having issues with file formats:

1. **Convert to PDF**: Most reliable format
2. **Check file size**: Must be under 10MB
3. **Verify file extension**: Must be .pdf, .docx, or .txt
4. **Test with sample file**: Use a simple .txt file to verify system works

## Sample Test File

Create a test file (`test.txt`):

```
John Doe
Software Engineer
john@example.com

EXPERIENCE
Senior Developer at Tech Corp (2020-Present)
- Led development team
- Improved performance by 40%

EDUCATION
B.S. Computer Science, University (2018)

SKILLS
Python, JavaScript, React, FastAPI
```

Save as `test.txt` and upload to verify CV analyzer is working.

---

**Last Updated**: November 2024

