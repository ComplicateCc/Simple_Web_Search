import React, { useState } from 'react'
import { Container, Paper, TextField, Button, Typography, Box, CircularProgress, Alert, Stepper, Step, StepLabel, Accordion, AccordionSummary, AccordionDetails } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'

function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeStep, setActiveStep] = useState(0)
  const [optimizedQuery, setOptimizedQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('请输入搜索内容')
      return
    }

    setLoading(true)
    setError('')
    setResult('')

    try {
      setActiveStep(0)
      const response = await axios.post('http://localhost:8003/search', {
        query: query.trim()
      })
      
      // 更新优化后的查询词
      setOptimizedQuery(response.data.optimized_query || '')
      setActiveStep(1)
      
      // 更新搜索结果
      setSearchResults(response.data.search_results || [])
      setActiveStep(2)
      
      // 更新分析结果
      setResult(response.data.response)
      setActiveStep(3)
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
        <Box sx={{ my: 4 }}>
          <Stepper activeStep={activeStep}>
            <Step>
              <StepLabel>优化搜索查询</StepLabel>
            </Step>
            <Step>
              <StepLabel>执行Google搜索</StepLabel>
            </Step>
            <Step>
              <StepLabel>分析搜索结果</StepLabel>
            </Step>
          </Stepper>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress />
          </Box>
        </Box>
      )}

      {optimizedQuery && (
        <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            优化后的搜索词：
          </Typography>
          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
            {optimizedQuery}
          </Typography>
        </Paper>
      )}

      {searchResults.length > 0 && (
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>原始搜索结果 ({searchResults.length})</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {searchResults.map((result, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Typography variant="h6" component="h3">
                  <a href={result.link} target="_blank" rel="noopener noreferrer">
                    {result.title}
                  </a>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.link}
                </Typography>
                <Typography variant="body1">
                  {result.snippet}
                </Typography>
              </Box>
            ))}
          </AccordionDetails>
        </Accordion>
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