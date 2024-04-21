## Movie Recommender Display

Presents the results of a 1-to-1 mapping of movies to recommendations for those who enjoyed them. Results are populated from the `final_recs1.csv` which was produced by the AI model in `project_updated_2.ipynb`.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

Run with `npm start` in the project directory, and go to [http://localhost:3000](http://localhost:3000) in your browser.

![Screenshot 2024-04-21 at 12 32 44 PM](https://github.com/petersnicole/movie-recommender-display/assets/63528753/ff353073-5240-4fe5-9ce9-34032fe3b374)



The code for the project is located within the final code folder of this repo. model_train.py is used for creating and training our model. project_viz.ipynb is used for analyzing and visualizing the results and get_recs.ipynb is used for getting recommendations for any number of input movies.

Due to file size restrictions, we were not able to upload the files to run model training or get model results for multiple inputs to Git Hub.

In order to create your own version of the model, download the movie lens data set from this [link](https://grouplens.org/datasets/movielens/25m/). You will need to use the ratings and genome score data frames for model training. You can then run as currently constructed to train in the same way that our final model was trained or change various parameters to construct your own version.

In order to get recommendations from multiple movie inputs, use get_recs.ipynb. You will need to download the final q table from [here](https://drive.google.com/file/d/1J00u3FMNURz9NArmUj6DQDp6VtuP8P2h/view?usp=sharing). You need to use movie ids as inputs, which can be found in movies_2428.csv.
