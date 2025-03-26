import React, { useState, useEffect } from 'react';
import { Dropdown, Alert, Spinner } from 'react-bootstrap';
import PaperCard from '../components/PaperCard';

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendedTitles = (): Set<string> => {
    const storedTitles = localStorage.getItem('recommendedPaperTitles');
    return storedTitles ? new Set(JSON.parse(storedTitles)) : new Set();
  };

  const [recommendedTitles, setRecommendedTitles] = useState<Set<string>>(getRecommendedTitles());

  const clearRecommendationHistory = () => {
    localStorage.removeItem('recommendedPaperTitles');
    setRecommendedTitles(new Set());
  };

  const fetchRecommendations = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = forceRefresh 
        ? '/api/recommendations/random/force-refresh'
        : '/api/recommendations/random';
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`请求失败: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      const uniqueRecommendations: Paper[] = [];
      const seenTitles = new Set<string>();
      const seenDOIs = new Set<string>();
      const seenTitleAuthorPairs = new Set<string>();
      
      for (const paper of data) {
        const titleAuthorPair = `${paper.title}::${paper.authors.join(',')}`;
        
        if (
          recommendedTitles.has(paper.title) || 
          seenTitles.has(paper.title) || 
          seenDOIs.has(paper.doi) || 
          seenTitleAuthorPairs.has(titleAuthorPair)
        ) {
          continue;
        }
        
        seenTitles.add(paper.title);
        if (paper.doi) seenDOIs.add(paper.doi);
        seenTitleAuthorPairs.add(titleAuthorPair);
        
        uniqueRecommendations.push(paper);
      }
      
      if (uniqueRecommendations.length > 0) {
        setRecommendations(uniqueRecommendations);
        
        const newRecommendedTitles = new Set(recommendedTitles);
        uniqueRecommendations.forEach(paper => {
          newRecommendedTitles.add(paper.title);
        });
        
        localStorage.setItem(
          'recommendedPaperTitles', 
          JSON.stringify([...newRecommendedTitles])
        );
        
        setRecommendedTitles(newRecommendedTitles);
      } else {
        setError("没有新的推荐文章。考虑清除历史记录以查看更多推荐。");
      }
    } catch (err) {
      setError(`获取推荐失败: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h1>文章推荐</h1>
        <div className="recommendations-actions">
          <Dropdown>
            <Dropdown.Toggle variant="primary" id="refresh-dropdown">
              刷新推荐
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item onClick={() => fetchRecommendations(false)}>缓存更新</Dropdown.Item>
              <Dropdown.Item onClick={() => fetchRecommendations(true)}>强制更新</Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item onClick={clearRecommendationHistory}>
                清除历史记录
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {loading ? (
        <div className="loading-container">
          <Spinner animation="border" />
        </div>
      ) : (
        <div className="recommendations-grid">
          {recommendations.length > 0 ? (
            recommendations.map((paper) => (
              <PaperCard key={paper.doi || paper.id || paper.title} paper={paper} />
            ))
          ) : (
            <div className="no-recommendations">
              <p>没有可显示的推荐。尝试刷新或清除历史记录。</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Recommendations; 