import React from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Heading,
  theme,
} from '@chakra-ui/react';
import { RecommendedMovieDisplay } from './RecommendedMovieDisplay';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">
        <VStack spacing={4}>
        <Heading as='h2'>
          Movie Recommender
        </Heading>
        <Heading as='h4' size='sm'>
          By group 17: Nicole, Sarah, Andres, and Jacob
        </Heading>
        <RecommendedMovieDisplay />
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App;
