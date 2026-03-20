using System.Net.Http.Json;
using Microsoft.Extensions.Logging;

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
            var response = await _httpClient.PostAsJsonAsync("http://172.193.60.120/recommend", payload);

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

    private void OnEntryFocused(object sender, FocusEventArgs e)
    {
        var entry = sender as Entry;
        entry.TextColor = Color.FromArgb("#845BFF"); // primary highlight
    }

    private void OnEntryUnfocused(object sender, FocusEventArgs e)
    {
        var entry = sender as Entry;
        entry.TextColor = Color.FromArgb("#222222");
    }

    private void OnPickerFocused(object sender, FocusEventArgs e)
    {
        var picker = sender as Picker;
        picker.TextColor = Color.FromArgb("#845BFF"); // highlight text
    }

    private void OnPickerUnfocused(object sender, FocusEventArgs e)
    {
        var picker = sender as Picker;
        picker.TextColor = Color.FromArgb("#222222");
    }

    private void OnButtonPressed(object sender, EventArgs e)
    {
        var button = sender as Button;
        button.BackgroundColor = Color.FromArgb("#6F47E0"); // slightly darker purple
        button.TextColor = Color.FromArgb("#F9F9F9");       // light text
    }

    private void OnButtonReleased(object sender, EventArgs e)
    {
        var button = sender as Button;
        button.BackgroundColor = Color.FromArgb("#845BFF");
        button.TextColor = Color.FromArgb("#FFFFFF");
    }
}

public class MovieResult
{
    public string Title { get; set; }
    public string Poster { get; set; }
    public string Description { get; set; }
}

