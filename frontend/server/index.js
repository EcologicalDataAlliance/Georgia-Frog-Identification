import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { createClient } from '@supabase/supabase-js'

// Load environment variables
dotenv.config()

const app = express()
const PORT = process.env.PORT || 8000

// Middleware
app.use(cors())
app.use(express.json())

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// Get public URLs for species media (audio and image)
app.get('/api/species/:slug/media', async (req, res) => {
  try {
    const { slug } = req.params
    const bucketName = 'Species Catalog'
    
    // Generate paths based on the structure: audio/slug_name/slug_name.mp3
    const audioPath = `audio/${slug}/${slug}.mp3`
    const imagePath = `images/${slug}/${slug}.jpg`
    
    // Get public URLs for public bucket
    const { data: audioData } = supabase
      .storage
      .from(bucketName)
      .getPublicUrl(audioPath)
    
    const { data: imageData } = supabase
      .storage
      .from(bucketName)
      .getPublicUrl(imagePath)
    
    // Return public URLs
    res.json({
      slug,
      audio: audioData.publicUrl,
      image: imageData.publicUrl,
      errors: {
        audio: null,
        image: null
      }
    })
  } catch (error) {
    console.error('Error generating public URLs:', error)
    res.status(500).json({ 
      error: 'Failed to generate public URLs', 
      message: error.message 
    })
  }
})

// Get all species media (batch endpoint for efficiency)
app.post('/api/species/media/batch', async (req, res) => {
  try {
    const { slugs } = req.body
    
    if (!Array.isArray(slugs)) {
      return res.status(400).json({ error: 'slugs must be an array' })
    }
    
    const bucketName = 'Species Catalog'
    const results = {}
    
    // Generate public URLs for each slug
    for (const slug of slugs) {
      const audioPath = `audio/${slug}/${slug}.mp3`
      const imagePath = `images/${slug}/${slug}.jpg`
      
      const { data: audioData } = supabase.storage.from(bucketName).getPublicUrl(audioPath)
      const { data: imageData } = supabase.storage.from(bucketName).getPublicUrl(imagePath)
      
      results[slug] = {
        audio: audioData.publicUrl,
        image: imageData.publicUrl,
        errors: {
          audio: null,
          image: null
        }
      }
    }
    
    res.json(results)
  } catch (error) {
    console.error('Error generating batch public URLs:', error)
    res.status(500).json({ 
      error: 'Failed to generate batch public URLs', 
      message: error.message 
    })
  }
})

// List files in a bucket (useful for debugging)
app.get('/api/storage/list/:folder?', async (req, res) => {
  try {
    const folder = req.params.folder || ''
    const bucketName = 'Species Catalog'
    
    const { data, error } = await supabase
      .storage
      .from(bucketName)
      .list(folder, {
        limit: 100,
        offset: 0
      })
    
    if (error) {
      return res.status(400).json({ error: error.message, bucketName, folder })
    }
    
    res.json({ folder: folder || 'root', bucketName, files: data })
  } catch (error) {
    console.error('Error listing files:', error)
    res.status(500).json({ 
      error: 'Failed to list files', 
      message: error.message 
    })
  }
})

// List all buckets (useful for debugging)
app.get('/api/storage/buckets', async (req, res) => {
  try {
    const { data, error } = await supabase
      .storage
      .listBuckets()
    
    if (error) {
      return res.status(400).json({ error: error.message })
    }
    
    res.json({ buckets: data })
  } catch (error) {
    console.error('Error listing buckets:', error)
    res.status(500).json({ 
      error: 'Failed to list buckets', 
      message: error.message 
    })
  }
})

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`)
  console.log(`Supabase URL: ${supabaseUrl}`)
  console.log(`Bucket: Species Catalog`)
})
