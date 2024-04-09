import { useState, useEffect } from "react";
import { Text, Button, VStack } from "@chakra-ui/react";
import Papa from 'papaparse';
import Select from 'react-select';

export function RecommendedMovieDisplay() {
  const [movies, setMovies] = useState([]);
  const [selectedMovies, setSelectedMovies] = useState([]);
  const [beforeMovies, setBeforeMovies] = useState([]);
  const [recomendedMovie, setRecomendedMovie] = useState('');

  const handleRecommend = (movieChoices) => {
    setBeforeMovies(movieChoices);
    // TODO: change this to instead pass all movie choices
    setRecomendedMovie(movies.filter(m => m['movie name'] === movieChoices[0])[0]['recomendation name']);
  }

  // copied from https://stackoverflow.com/questions/53416529/react-import-csv-file-and-parse
  useEffect(() => {
    async function getData() {
        const response = await fetch('/recomendation_after_1000_episodes_v1.csv')
        const reader = response.body.getReader()
        const result = await reader.read() // raw array
        const decoder = new TextDecoder('utf-8')
        const csv = decoder.decode(result.value) // the csv text
        const results = Papa.parse(csv, { header: true }) // object with { data, errors, meta }
        const rows = results.data // array of objects
        setMovies(rows)
    }
    getData()
  }, []) // [] means just do this once, after initial render

  const options = movies.map((movie, index) => ({value: index, label: movie['movie name']}))

  return (
    <VStack>
        <Button onClick={() => {handleRecommend([movies[Math.floor(Math.random() * movies.length)]['movie name']])}}>Get Recommendation for Random Movie</Button>
        <Text>Or</Text>
        <div style={{ width: '100%' }}><Select onChange={(selectedOptions) => setSelectedMovies(selectedOptions.map((movie) => movie.label))} placeholder='Choose movie' options={options} isMulti/></div>
        <Button onClick={() => {handleRecommend(selectedMovies)}}>Get Recommendation</Button>
        <Text>Recommendation for</Text>
        <Text>{beforeMovies.join(', ')}</Text>
        <Text>is</Text>
        <Text>{recomendedMovie}</Text>
    </VStack>
  );
}