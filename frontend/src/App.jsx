import React, { useState } from 'react'
import { Container, Paper, TextField, Button, Typography, Box, CircularProgress, Alert } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'

function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('请输入搜索内容')
      return
    }

    setLoading(true)
    setError('')
    setResult('')

    try {
      const response = await axios.post('http://localhost:8003/search', {
        query: query.trim()
      })
      setResult(response.data.response)
    } catch (err) {
      setError('搜索请求失败，请稍后重试')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" align="center" gutterBottom>
        AI智能搜索
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="请输入您的问题..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleSearch}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
          >
            搜索
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {result && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <ReactMarkdown>{result}</ReactMarkdown>
        </Paper>
      )}
    </Container>
  )
}

export default App