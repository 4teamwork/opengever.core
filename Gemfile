source 'https://rubygems.org'
ruby '2.4.5'
gem 'sass', '~> 3.4'

install_if -> { RUBY_PLATFORM =~ /darwin|bsd|dragonfly/ } do
  gem 'rb-kqueue', '>= 0.2'
end

install_if -> { RUBY_PLATFORM =~ /linux/ } do
    # Should just work, leaving for documentation completenes
end

install_if -> { (RUBY_PLATFORM =~ /cygwin|mswin|mingw|bccwin|wince|emx/) != nil } do
  gem 'wdm', '>= 0.1.0'
end
