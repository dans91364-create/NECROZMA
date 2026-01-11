    # Test Mode arguments
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with sampled data"
    )
    
    parser.add_argument(
        "--test-strategy",
        type=str,
        default="balanced",
        choices=["minimal", "quick", "balanced", "thorough"],
        help="Test sampling strategy (default: balanced)"
    )
    
    parser.add_argument(
        "--test-weeks",
        type=int,
        default=4,
        help="Number of weeks to sample for testing (default: 4)"
    )
    
    parser.add_argument(
        "--test-seed",
        type=int,
        default=42,
        help="Random seed for reproducible test samples (default: 42)"
    )
    
    parser.add_argument(
        "--strategy-discovery",
        action="store_true",
        help="Run complete strategy discovery pipeline (labeling, regime detection, backtesting, ranking)"
    )
    
    parser.add_argument(
        "--skip-telegram",
        action="store_true",
        help="Disable Telegram notifications"
    )
    
    return parser.parse_args()