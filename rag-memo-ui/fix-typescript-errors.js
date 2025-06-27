#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Files to fix
const filesToFix = [
  'src/app/dashboard/page.tsx',
  'src/app/elements/create/page.tsx', 
  'src/app/elements/page.tsx',
  'src/app/evaluations/page.tsx',
  'src/app/generations/[id]/page.tsx',
  'src/app/generations/page.tsx',
  'src/app/projects/[id]/page.tsx',
  'src/components/documents/DocumentList.tsx',
  'src/components/testing/APITestSuite.tsx',
  'src/lib/api/documentApi.ts',
  'src/store/index.ts',
  'src/utils/testHelpers.ts'
];

console.log('Fixing TypeScript errors...');

filesToFix.forEach(file => {
  const filePath = path.join(__dirname, file);
  
  if (!fs.existsSync(filePath)) {
    console.log(`Skipping ${file} - file not found`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Fix document.title -> document.filename
  content = content.replace(/doc\.title/g, 'doc.filename');
  content = content.replace(/document\.title/g, 'document.filename');
  
  // Fix document.file_type -> document.content_type
  content = content.replace(/doc\.file_type/g, 'doc.content_type');
  content = content.replace(/document\.file_type/g, 'document.content_type');
  
  // Fix element.last_executed references
  content = content.replace(/element\.last_executed \? new Date\(element\.last_executed\)\.toLocaleDateString\(\) : 'Never'/g, "'Never'");
  content = content.replace(/element\.last_executed/g, 'undefined');
  
  // Fix element.type references (doesn't exist in backend)
  content = content.replace(/element\.type/g, 'element.element_type');
  
  // Fix ElementStatus.ARCHIVED
  content = content.replace(/ElementStatus\.ARCHIVED/g, 'ElementStatus.DEPRECATED');
  
  // Fix error_message: null -> error_message: undefined
  content = content.replace(/error_message: null/g, 'error_message: undefined');
  content = content.replace(/output_text: null/g, 'output_text: undefined');
  
  // Fix possibly undefined access
  content = content.replace(/generation\.element_name\.toLowerCase\(\)/g, 'generation.element_name?.toLowerCase() || ""');
  content = content.replace(/generation\.model_used\.toLowerCase\(\)/g, 'generation.model_used?.toLowerCase() || ""');
  content = content.replace(/element\.description\.toLowerCase\(\)/g, 'element.description?.toLowerCase() || ""');
  
  // Fix template_content field
  content = content.replace(/template_content:/g, 'content:');
  
  fs.writeFileSync(filePath, content);
  console.log(`Fixed ${file}`);
});

console.log('TypeScript error fixes completed!'); 