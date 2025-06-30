IF DB_ID('AppDB') IS NULL
BEGIN
    CREATE DATABASE AppDB;
END
GO

USE AppDB;
GO


CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    UserName NVARCHAR(50) NOT NULL UNIQUE,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(256) NOT NULL,
    CreationDate DATETIME DEFAULT GETDATE()
);

CREATE TABLE dbo.Artists (
    ArtistID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    ArtistName NVARCHAR(100) NOT NULL
);

CREATE TABLE dbo.Albums (
    AlbumID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    AlbumTitle NVARCHAR(100) NOT NULL,
    ArtistID INT NOT NULL,
    ReleaseYear INT NULL,
    CoverImageUrl NVARCHAR(255) NULL,
    SongCount INT DEFAULT 0,
    CONSTRAINT FK_Albums_Artists FOREIGN KEY (ArtistID) REFERENCES dbo.Artists(ArtistID) ON DELETE CASCADE
);

CREATE TABLE dbo.Songs (
    SongID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    SongTitle NVARCHAR(150) NOT NULL,
    AlbumID INT NOT NULL,
    DurationSeconds INT NOT NULL,
    AudioUrl NVARCHAR(255) NULL,
    CoverArtUrl NVARCHAR(255) NULL,
    CONSTRAINT FK_Songs_Albums FOREIGN KEY (AlbumID) REFERENCES dbo.Albums(AlbumID) ON DELETE CASCADE,
    CONSTRAINT CHK_DurationSeconds CHECK (DurationSeconds > 0)
);

CREATE TABLE dbo.Playlists (
    PlaylistID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    PlaylistName NVARCHAR(100) NOT NULL,
    UserID INT NOT NULL,
    CreationDate DATETIME DEFAULT GETDATE(),
    CoverImageUrl NVARCHAR(255) NULL,
    CONSTRAINT FK_Playlists_Users FOREIGN KEY (UserID) REFERENCES dbo.Users(UserID) ON DELETE CASCADE
);

CREATE TABLE dbo.PlaylistSongs (
    PlaylistID INT NOT NULL,
    SongID INT NOT NULL,
    DateAdded DATETIME DEFAULT GETDATE(),
    CONSTRAINT PK_PlaylistSongs PRIMARY KEY (PlaylistID, SongID),
    CONSTRAINT FK_PlaylistSongs_Playlists FOREIGN KEY (PlaylistID) REFERENCES dbo.Playlists(PlaylistID) ON DELETE CASCADE,
    CONSTRAINT FK_PlaylistSongs_Songs FOREIGN KEY (SongID) REFERENCES dbo.Songs(SongID) ON DELETE CASCADE
);

CREATE TABLE dbo.PlaylistAuditLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    PlaylistID INT NOT NULL,
    PlaylistName NVARCHAR(100),
    DeletedBy NVARCHAR(100),
    DeletionDate DATETIME DEFAULT GETDATE()
);
GO


CREATE PROCEDURE dbo.sp_CreateArtist @ArtistName NVARCHAR(100), @NewArtistID INT OUTPUT AS BEGIN INSERT INTO dbo.Artists (ArtistName) VALUES (@ArtistName); SET @NewArtistID = SCOPE_IDENTITY(); END;
GO
CREATE PROCEDURE dbo.sp_CreateAlbum @AlbumTitle NVARCHAR(100), @ArtistID INT, @ReleaseYear INT, @NewAlbumID INT OUTPUT AS BEGIN INSERT INTO dbo.Albums (AlbumTitle, ArtistID, ReleaseYear) VALUES (@AlbumTitle, @ArtistID, @ReleaseYear); SET @NewAlbumID = SCOPE_IDENTITY(); END;
GO
CREATE PROCEDURE dbo.sp_CreateSong @SongTitle NVARCHAR(150), @AlbumID INT, @DurationSeconds INT, @NewSongID INT OUTPUT AS BEGIN INSERT INTO dbo.Songs (SongTitle, AlbumID, DurationSeconds) VALUES (@SongTitle, @AlbumID, @DurationSeconds); SET @NewSongID = SCOPE_IDENTITY(); END;
GO
CREATE PROCEDURE dbo.sp_AddSongToPlaylist @PlaylistID INT, @SongID INT AS BEGIN IF NOT EXISTS (SELECT 1 FROM dbo.PlaylistSongs WHERE PlaylistID = @PlaylistID AND SongID = @SongID) BEGIN INSERT INTO dbo.PlaylistSongs (PlaylistID, SongID) VALUES (@PlaylistID, @SongID); END END;
GO
CREATE PROCEDURE dbo.sp_GetAllSongs AS BEGIN SET NOCOUNT ON; SELECT s.SongID, s.SongTitle, a.AlbumTitle, ar.ArtistName, s.DurationSeconds, s.AudioUrl, s.CoverArtUrl FROM dbo.Songs s LEFT JOIN dbo.Albums a ON s.AlbumID = a.AlbumID LEFT JOIN dbo.Artists ar ON a.ArtistID = ar.ArtistID ORDER BY s.SongID DESC; END;
GO
CREATE PROCEDURE dbo.sp_GetSongsInPlaylist @PlaylistID INT AS BEGIN SET NOCOUNT ON; SELECT s.SongID, s.SongTitle, a.AlbumTitle, ar.ArtistName, s.DurationSeconds, s.AudioUrl, s.CoverArtUrl FROM dbo.Songs s JOIN dbo.PlaylistSongs ps ON s.SongID = ps.SongID JOIN dbo.Albums a ON s.AlbumID = a.AlbumID JOIN dbo.Artists ar ON a.ArtistID = ar.ArtistID WHERE ps.PlaylistID = @PlaylistID; END;
GO
CREATE PROCEDURE dbo.sp_GetUserPlaylists @UserID INT AS BEGIN SET NOCOUNT ON; SELECT PlaylistID, PlaylistName, UserID, CreationDate, CoverImageUrl FROM dbo.Playlists WHERE UserID = @UserID; END;
GO
CREATE PROCEDURE dbo.sp_UpdatePlaylistName @PlaylistID INT, @NewPlaylistName NVARCHAR(100) AS BEGIN SET NOCOUNT ON; UPDATE dbo.Playlists SET PlaylistName = @NewPlaylistName WHERE PlaylistID = @PlaylistID; END;
GO
CREATE PROCEDURE dbo.sp_UpdatePlaylistCover @PlaylistID INT, @CoverImageUrl NVARCHAR(255) AS BEGIN SET NOCOUNT ON; UPDATE dbo.Playlists SET CoverImageUrl = @CoverImageUrl WHERE PlaylistID = @PlaylistID; END;
GO


CREATE FUNCTION dbo.fn_GetPlaylistTotalDuration (@PlaylistID INT) RETURNS INT AS BEGIN DECLARE @TotalDuration INT; SELECT @TotalDuration = SUM(s.DurationSeconds) FROM dbo.PlaylistSongs ps JOIN dbo.Songs s ON ps.SongID = s.SongID WHERE ps.PlaylistID = @PlaylistID; RETURN ISNULL(@TotalDuration, 0); END;
GO


CREATE TRIGGER dbo.trg_UpdateAlbumSongCount ON dbo.Songs AFTER INSERT, DELETE AS BEGIN SET NOCOUNT ON; UPDATE A SET A.SongCount = A.SongCount + I.NumberOfSongs FROM dbo.Albums AS A JOIN (SELECT AlbumID, COUNT(*) AS NumberOfSongs FROM inserted GROUP BY AlbumID) AS I ON A.AlbumID = I.AlbumID; UPDATE A SET A.SongCount = A.SongCount - D.NumberOfSongs FROM dbo.Albums AS A JOIN (SELECT AlbumID, COUNT(*) AS NumberOfSongs FROM deleted GROUP BY AlbumID) AS D ON A.AlbumID = D.AlbumID; END;
GO
CREATE TRIGGER dbo.trg_AuditPlaylistDeletion ON dbo.Playlists FOR DELETE AS BEGIN SET NOCOUNT ON; INSERT INTO dbo.PlaylistAuditLog (PlaylistID, PlaylistName, DeletedBy) SELECT d.PlaylistID, d.PlaylistName, SUSER_SNAME() FROM deleted d; END;
GO


IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE UserName = 'test')
BEGIN
    INSERT INTO dbo.Users (UserName, Email, PasswordHash) VALUES ('test', 'test@test.com', '123456');
END
IF NOT EXISTS (SELECT 1 FROM dbo.Artists WHERE ArtistName = 'Deneme') INSERT INTO dbo.Artists (ArtistName) VALUES ('Deneme');
DECLARE @ArtistID_Deneme INT = (SELECT ArtistID FROM dbo.Artists WHERE ArtistName = 'Deneme');
IF NOT EXISTS (SELECT 1 FROM dbo.Albums WHERE AlbumTitle = 'Deneme Albümü') INSERT INTO dbo.Albums (AlbumTitle, ArtistID, ReleaseYear) VALUES ('Deneme Albümü', @ArtistID_Deneme, 1976);
