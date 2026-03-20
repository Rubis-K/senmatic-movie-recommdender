namespace MauiApp1
{
    public partial class App : Application
    {
        public App()
        {
            InitializeComponent();

        
        }

        protected override Window CreateWindow(IActivationState activationState)
        {
            // Instead of MainPage = new AppShell();
            return new Window(new AppShell());
        }
    }
}
