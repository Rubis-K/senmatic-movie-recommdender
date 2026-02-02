using System.Net.Http.Json;

namespace MauiApp1;

public partial class MainPage : ContentPage
{
    private readonly HttpClient _httpClient = new HttpClient();

    public MainPage()
    {
        InitializeComponent();

        // Populate category and tone pickers
        CategoryPicker.ItemsSource = new List<string> { "All", "serious", "entertainment", "other" }; 
        TonePicker.ItemsSource = new List<string> { "All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad" };
    }

    private async void OnGetMoviesClicked(object sender, EventArgs e)
    {
        try
        {
            string query = QueryEntry.Text ?? "";
            string category = CategoryPicker.SelectedItem?.ToString() ?? "All";
            string tone = TonePicker.SelectedItem?.ToString() ?? "All";

            var payload = new { query = query, category = category, tone = tone };
            var response = await _httpClient.PostAsJsonAsync("https://movierecommenderapi.azurewebsites.net/", payload);

            if (response.IsSuccessStatusCode)
            {
                var movies = await response.Content.ReadFromJsonAsync<List<MovieResult>>();
                MoviesListView.ItemsSource = movies;
            }
            else
            {
                await DisplayAlert("Error", "Failed to get movies from API", "OK");
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", ex.Message, "OK");
        }
    }
}

public class MovieResult
{
    public string Title { get; set; }
    public string Poster { get; set; }
    public string Description { get; set; }
}